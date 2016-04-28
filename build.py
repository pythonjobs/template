#!/usr/bin/env python2.7
import re
import sys
import shutil
import os
import os.path
import subprocess
import yaml
from fin.contextlog import Log


def validate(fullpath):
    """Validate the formatting of the given jobs file.

    The contents of the file will be validated later; this is just checking
    that the file will parse.

    """
    data = open(fullpath, 'r').read()
    path = os.path.basename(fullpath)

    try:
        data = data.decode('utf8')
    except UnicodeDecodeError:
        raise AssertionError("%s: is not valid UTF-8" % path)
    chunks = re.split(r'^---[ \t]*$', data, flags=re.M)
    assert len(chunks) >= 3, \
        "%s: should be YAML and Markdown, prefixed by --- lines" % path
    assert not chunks[0].strip(), \
        "%s: data before initial ---" % path

    try:
        yaml.safe_load(chunks[1])
    except Exception as e:
        raise AssertionError("%s: malformed YAML: %s" % (path, e))


def main(jobs_dir):
    with Log("Identifying paths"):
        jobs_root = os.path.abspath(jobs_dir)
        template_dir = os.path.abspath(os.path.dirname(__file__))
        hyde_root = os.path.join(template_dir, 'hyde')
        jobs_source = os.path.join(jobs_root, 'jobs')
        jobs_dest = os.path.join(hyde_root, 'content', 'jobs')
        deploy_dir = os.path.join(hyde_root, 'deploy')
        jobs_meta_path = os.path.join(jobs_dest, 'meta.yaml')

    with Log("Copy in jobs") as l:
        for file in os.listdir(jobs_source):
            assert file.endswith(".html"), \
                "%s: jobs files must end in .html" % file
            with Log('Copying %s' % file):
                src_path = '%s/%s' % (jobs_source, file) # This is safer than join()
                dest_path = '%s/%s' % (jobs_dest, file)
                validate(src_path)
                shutil.copyfile(src_path, dest_path)

    with Log("Building Site"):
        subprocess.check_call(['hyde', '-x', '-s', hyde_root, 'gen', '-r'])


if __name__ == "__main__":
    # using sys.argv like this is ugly
    sys.exit(main(*sys.argv[1:]))
