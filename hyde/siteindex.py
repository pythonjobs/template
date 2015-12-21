# -*- coding: utf-8 -*-
import os
import operator
import collections
import json
import bs4
import stemming.porter2 as porter2
import re

from fin.contextlog import Log, CLog
import fin.cache
import hyde.plugin
import jinja2
from fswrap import File


class Tree(object):

    def __init__(self):
        self.tree = {}

    def add(self, word, resources):
        base = self.tree
        for char in word:
            base.setdefault(char, ({}, {}))
            nodes, base = base[char]
        for key, value in resources:
            nodes.setdefault(key, 0)
            nodes[key] += value

    def collapse(self, theshold, start=None):
        # Note: threshold isn't currently used, but could be used to get rid of terms that are
        # /too/ common.
        if start is None:
            out = {}
            for prefix, children in self.tree.iteritems():
                new_prefix, children = self.collapse(theshold, children)
                if new_prefix == "":
                    out[prefix] = children
                else:
                    out[prefix] = {new_prefix: children}
            return out
        matches, children = start
        if len(matches) == 0 and len(children) == 1:
            child_prefix, new_val = self.collapse(theshold, children.values()[0])
            return (children.keys()[0] + child_prefix, new_val)
        else:
            sorted_matches = sorted(matches.items(), key=operator.itemgetter(1), reverse=True)
            out = {}
            if sorted_matches:
                out[''] = sorted_matches
            for child_prefix, value in children.iteritems():
                new_prefix, new_value = self.collapse(theshold, start=value)
                out[child_prefix + new_prefix] = new_value
            if out.keys() == ['']:
                out = out['']
            return "", out


class IndexerPlugin(hyde.plugin.Plugin):
    INDEX_FREQUENCY_LIMIT = 0.45 # if word appear in more than this proportion of jobs, ignore it

    def __init__(self, site):
        super(IndexerPlugin, self).__init__(site)
        self.jobs_dir = os.path.join(self.site.sitepath.path, "content", "jobs")
        self.resources = []
        self.by_word = collections.defaultdict(lambda: collections.defaultdict(int))

    def add_to_index(self, resource, texts):
        resource_index = len(self.resources)
        self.resources.append(resource.slug)
        for _, text, weight in texts:
            words = re.split(r"\W+", text, flags=re.U)
            for word in words:
                if word == "" or word.isdigit():
                    continue
                stemmed = porter2.stem(word.lower())
                if len(stemmed) < 2:
                    continue
                self.by_word[stemmed][resource_index] += weight

    def text_resource_complete(self, resource, text):
        with CLog("Indexing %s" % resource):
            if not resource.source_file.kind == 'html':
                return
            if not resource.source_file.is_descendant_of(self.jobs_dir):
                return

            doc = bs4.BeautifulSoup(text, "html.parser")
            body = doc.find(attrs={"class": 'body'})
            headings = body.select("h1,h2")
            for heading in headings:
                heading.extract()
            tags = " ".join(resource.meta.get('tags', ''))
            company = resource.meta.get('company', '')
            title = resource.meta.get('title', '')
            parts = [
                ("Title: ",title, 10),
                ("Company: ",company, 5),
                ("Tags: ", tags, 5),
                ("", body.text, 1),
            ]
            self.write_text_resource(resource.slug, parts)
            self.add_to_index(resource, parts)

    def write_text_resource(self, name, parts):
        text_content = []
        for prefix, content, _ in parts:
            collapsed_content = " ".join(content.splitlines()).strip()
            text_content.append("%s%s" % (prefix, collapsed_content))
        text_content = ".\n".join(text_content)
        self.deploy(text_content, "excerpts/%s.txt" % (name, ))

    def deploy(self, content, rel_path):
        with CLog("Deploying file: %s" % rel_path):
            with CLog("Updating resource"):
                target = self.site.config.content_root_path.child_file(rel_path)
                res = self.site.content.add_resource(target)
                target.parent.make()
                with open(target.path, "wb") as fh:
                    fh.write(content.encode("utf-8"))
            with CLog("Copying to dest"):
                # Because this is called from node_complete, it's too late to let the deployer
                # copy the file for us, so have to do it manually
                target = File(self.site.config.deploy_root_path.child(res.relative_deploy_path))
                target.parent.make()
                res.source_file.copy_to(target)

    def node_complete(self, node):
        if node.path != self.jobs_dir:
            return
        with Log("Building Full-Text index"):
            num_resource = len(self.resources)
            threshold = num_resource * self.INDEX_FREQUENCY_LIMIT
            tree = Tree()
            for word, by_resource in self.by_word.iteritems():
                tree.add(word, by_resource.items())
            self.write_index((self.resources, tree.collapse(threshold)))

    def write_index(self, index):
        with Log("Encoding as JSON") as l:
            data = json.dumps(index, separators=",:")
            l.output("%s bytes" % len(data))
        self.deploy(data, "text_index.json")
