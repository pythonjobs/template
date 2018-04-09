# -*- coding: utf-8 -*-

import datetime
import os
import collections
import requests
import json
import re
import traceback
import urllib
from fin.contextlog import Log
import fin.cache
import hyde.plugin
from hyde.exceptions import HydeException


# Bit ugly, but patch HydeException to not mangle all exception on reraise
# which was causing confusing error messages:
_orig_reraise = HydeException.reraise
def new_reraise(message, exc_info):
    tp, exc, tb = exc_info
    if isinstance(exc, HydeException):
        raise tp, exc, tb
    _orig_reraise(message, exc_info)
HydeException.reraise = staticmethod(new_reraise)


COMMENT_TEMPLATE = """Hi

Thanks for submitting this job advert.

We've run a few automated tests and discovered %s:

%s

If you'd like some help correcting this, or think the error is incorrect, please reply to this comment.

Thanks

Pythonjobs
"""


ONE_YEAR_AGO = datetime.date.today() - datetime.timedelta(days=365)

class LocationFinder(object):
    PUBLISHED_LOCATIONS = 'http://pythonjobs.github.io/media/geo.json'
    API_URL = 'http://maps.googleapis.com/maps/api/geocode/json'

    def _get_json(self, url):
        with Log('Getting %s' % url):
            res = urllib.urlopen(url)
            if res.code != 200:
                return {}
            try:
                return json.load(res)
            except:
                return {}

    @fin.cache.property
    def known_locations(self):
        return self._get_json(self.PUBLISHED_LOCATIONS)

    def query_location(self, location):
        query = urllib.urlencode({'address': location})
        url = self.API_URL + '?' + query
        data = self._get_json(url)
        results = data.get('results', [])
        if not results:
            return None
        best_match = results[0]
        return best_match.get('geometry', {}).get('location', None)

    def find_location(self, location):
        if location in self.known_locations:
            return self.known_locations[location]
        with Log("Querying Google API for location"):
            result = self.query_location(location)
            if result:
                self.known_locations[location] = result
            return result


class CheckMetaPlugin(hyde.plugin.Plugin):

    @fin.cache.property
    def errors(self):
        return collections.defaultdict(list)

    @fin.cache.property
    def location_finder(self):
        return LocationFinder()

    def _get_testers(self):
        for name in dir(self):
            if not name.startswith('test_'):
                continue
            value = getattr(self, name)
            if callable(value):
                yield value

    def check_meta_len(self, resource, field, min_length):
        parts = field.split('.')
        base = resource.meta
        for part in parts:
            base = getattr(base, part)
        var = (base or '').strip()
        if len(var) < min_length:
            self.add_error(
                resource,
                "Field %s: `%s` must be at least %s characters long",
                field,
                var,
                min_length
            )

    def test_title(self, resource):
        """ Jobs must have a title """
        self.check_meta_len(resource, "title", 3)

    def test_company(self, resource):
        """ Jobs must reference a company """
        self.check_meta_len(resource, "company", 2)

    def test_email(self, resource):
        """ Jobs must include a valid email """
        email = resource.meta.contact.email
        pattern = r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,10}$'
        if not re.match(pattern, email, re.I):
            self.add_error(
                resource,
                "We couldn't verify the contact email address: `%s`",
                email)

    def test_name(self, resource):
        """ Jobs must include a contact name"""
        self.check_meta_len(resource, "contact.name", 3)

    def test_location(self, resource):
        """ Jobs must include a location """
        self.check_meta_len(resource, "location", 3)

    VALID_CONTRACT_TYPES = set('contract,perm,temp,part-time,other'.split(','))

    def test_type(self, resource):
        """ Jobs must include a 'contract' type """
        contract_type = resource.meta.contract.strip().lower()
        have_any = any(
            val in contract_type for val in self.VALID_CONTRACT_TYPES)
        if not have_any:
            self.add_error(
                resource,
                "`contract` field: `%s` must contain one of: %s",
                resource.meta.contract,
                (', '.join(self.VALID_CONTRACT_TYPES))
            )

    def test_created_date(self, resource):
        """ Jobs must have a create date before now """
        date = resource.meta.created
        if not isinstance(date, datetime.date):
            return self.add_error(
                resource,
                "The `created` field must be provided, and contain a valid date. "
                "%s could not be interpreted as a valid date",
                date
            )

        # unfortunately isinstance fails us here
        if type(date) is not datetime.date:
            return self.add_error(
                resource, 'The `created` field created must be a date, not date time'
            )
        if resource.meta.created < ONE_YEAR_AGO:
            resource.is_processable = False  # Remove old job listings
        if date > datetime.date.today():
            return self.add_error(
                resource,
                "The `created` field %s is in the future",
                date
            )

    def test_no_index_tag(self, resource):
        """ Job tags must not include the tag 'index' """
        for tag in resource.meta.tags:
            if tag.strip().lower() == 'index':
                self.add_error(resource, "Tags cannot include 'index'")

    def test_correct_filename(self, resource):
        """ Job filename must end in .html """
        if not resource.name.lower().endswith('.html'):
            _, ext = os.path.splitext(resource.name)
            self.add_error(resource, "Job files must end with `.html`, not `%s`", ext)

    @staticmethod
    def fix_tag(tag):
        return tag.lower()  # .replace(" ", "_")
        # uncomment the last bit if we decide to disallow
        # spaces in tags

    def test_lookup_location(self, resource):
        """Get the latitude longitude values for this location"""
        # This is NOT a test, but performs useful per-node things
        location = getattr(resource.meta.contact, 'address', None)
        if location is None:
            location = resource.meta.location
        with Log("Finding job location"):
            coords = self.location_finder.find_location(location)
            if coords is not None:
                resource.meta._coords = coords

    def add_error(self, resource, message, *args):
        message_str = message % args
        self.errors[resource.name].append(message_str)

    def get_pr_comment(self):
        num_errors = 0
        lines = []
        for file, errors in self.errors.items():
            lines.append("\n**%s**:" % file)
            for error in errors:
                lines.append("* %s" % error)
                num_errors += 1
        plural = "an issue" if num_errors == 1 else "some issues"
        return COMMENT_TEMPLATE % (plural, "\n".join(lines))

    def begin_site(self):
        jobs = self.site.content.node_from_relative_path('jobs/')
        with Log("Checking jobs metadata") as l:
            for resource in jobs.walk_resources():
                if not resource.is_processable:
                    l.output("Skipping %s" % (resource.name, ))
                    continue
                with Log(resource.name):
                    # Ensure that all tags are lowercase
                    resource.meta.tags = [self.fix_tag(a)
                                          for a in resource.meta.tags]

                    for tester in self._get_testers():
                        docstring = tester.__doc__.strip()
                        assert docstring
                        with Log("Test %s" % (docstring, )):
                            tester(resource)

        if self.errors:
            if "GH_TOKEN" in os.environ and "TRAVIS_PULL_REQUEST" in os.environ:
                token = os.environ['GH_TOKEN']
                pr_num = os.environ["TRAVIS_PULL_REQUEST"]
                url = "https://api.github.com/repos/pythonjobs/jobs/issues/%s/comments" % pr_num
                req = requests.post(
                    url, json={"body": self.get_pr_comment()},
                    headers={"Authorization": "token %s" % token}
                )
                print(req.text)
                req.raise_for_status()
            with Log("Site Processing Errors"):
                for filename, errors in self.errors.items():
                    with Log(filename, ok_msg="x") as log:
                        for error in errors:
                            log.output(error)
                raise HydeException("Some job listings failed validation")
        self.site.locations = json.dumps(self.location_finder.known_locations)

