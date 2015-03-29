# -*- coding: utf-8 -*-

import datetime
import functools
import json
import re
import traceback
import urllib

from fin.contextlog import Log
import fin.cache
import hyde.plugin
import jinja2


def add_template_filters(site):
    site.config['jinja2']

class LocationFinder(object):
    PUBLISHED_LOCATIONS = 'http://pythonjobs.github.io/media/geo.json'
    API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

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
            Log.output("Location %s already known" % (location, ))
            return self.known_locations[location]
        with Log("Querying Google API for location"):
            result = self.query_location(location)
            if result:
                self.known_locations[location] = result
            return result
    

class CheckMetaPlugin(hyde.plugin.Plugin):

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

    def assertTrue(self, condition, message="Assertion Failed"):
        if not condition:
            raise AssertionError(message)

    def assertFalse(self, condition, message="Assertion Failed"):
        if condition:
            raise AssertionError(message)

    def test_title(self, resource):
        """ Jobs must have a title """
        self.assertTrue(len(resource.meta.title) > 3)

    def test_company(self, resource):
        """ Jobs must reference a company """
        self.assertTrue(len(resource.meta.company) > 2)

    def test_email(self, resource):
        """ Jobs must include a valid email """
        email = resource.meta.contact.email
        pattern = '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,10}$'
        self.assertTrue(
            re.match(pattern, email, re.I) is not None)

    def test_name(self, resource):
        """ Jobs must include a contact name"""
        contact = resource.meta.contact.name
        self.assertTrue(' ' in contact.strip())
        self.assertTrue(len(contact) > 3)

    def test_location(self, resource):
        """ Jobs must include a location """
        location = resource.meta.location
        self.assertTrue(len(location) >= 3)

    VALID_CONTRACT_TYPES = set('contract,perm,temp,part-time,other'.split(','))

    def test_type(self, resource):
        """ Jobs must include a 'contract' type """
        contract_type = resource.meta.contract.strip().lower()
        have_any = any(
            val in contract_type for val in self.VALID_CONTRACT_TYPES)
        self.assertTrue(have_any,
                        "'contract' must contain one of: %s" %
                        (', '.join(self.VALID_CONTRACT_TYPES)))

    def test_created_date(self, resource):
        """ Jobs must have a create date before now """
        date = resource.meta.created
        self.assertTrue(isinstance(date, datetime.date))

        # unfortunately isinstance fails us here
        self.assertTrue(type(date) is datetime.date,
                        'created must be a date, not date time')
        self.assertTrue(
            date <= datetime.date.today(), "%s is in the future" % date)

    def test_no_index_tag(self, resource):
        """ Job tags must not include the tag 'index' """
        for tag in resource.meta.tags:
            self.assertFalse(
                tag.strip().lower() == 'index', "Tags cannot include 'index'")

    def test_correct_filename(self, resource):
        """ Job filename must end in .html """
        self.assertTrue(resource.name.lower().endswith('.html'))

    @staticmethod
    def fix_tag(tag):
        return tag.lower()  # .replace(" ", "_")
        # uncomment the last bit if we decide to disallow
        # spaces in tags

    def lookup_location(self, resource):
        location = getattr(resource.meta.contact, 'address', None)
        if location is None:
            location = resource.meta.location
        with Log("Finding job location"):
            coords = self.location_finder.find_location(location)
            if coords is not None:
                Log.output(str(coords))
                resource.meta._coords = coords

    def begin_site(self):
        add_template_filters(self.site)
        jobs = self.site.content.node_from_relative_path('jobs/')
        with Log("Checking jobs metadata") as l:
            last_exc = None
            for resource in jobs.walk_resources():
                if not resource.is_processable:
                    l.output("Skipping %s" % (resource.name, ))
                    continue
                with Log(resource.name):

                    # Ensure that all tags are lowercase
                    resource.meta.tags = [self.fix_tag(a)
                                          for a in resource.meta.tags]

                    for tester in self._get_testers():
                        assert tester.__doc__ is not None
                        with Log("Test %s" % (tester.__doc__.strip())) as l2:
                            try:
                                tester(resource)
                            except Exception, e:
                                for line in traceback.format_exc().strip().splitlines():
                                    l2.output(line)
                                l2.ok_msg = l2.fail_msg
                                last_exc = e
                    self.lookup_location(resource)

            if last_exc is not None:
                raise last_exc
        self.site.locations = json.dumps(self.location_finder.known_locations)
