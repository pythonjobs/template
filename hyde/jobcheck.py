import hyde.plugin
import datetime
import re
from fin.contextlog import Log

class CheckMetaPlugin(hyde.plugin.Plugin):

	def _get_testers(self):
		tester_re = 'test_'
		for name in dir(self):
			if not name.startswith('test_'):
				continue
			value = getattr(self, name)
			if callable(value):
				yield value

	def assertTrue(self, condition, message="Assertion Failed"):
		if not condition:
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
		self.assertTrue(re.match('^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,10}$', email, re.I) is not None)

	def test_name(self, resource):
		""" Jobs must include a contact name"""
		contact = resource.meta.contact.name
		self.assertTrue(' ' in contact.strip())
		self.assertTrue(len(contact) > 3)

	def test_created_date(self, resource):
		""" Jobs must have a create date before now """
		date = resource.meta.created
		self.assertTrue(isinstance(date, datetime.date))
		self.assertTrue(type(date) is datetime.date, # unfortunately isinstance fails us here
						'created must be a date, not date time') 
		self.assertTrue(date < datetime.date.today(), "%s is in the future" % date)

	def begin_site(self):
		jobs = self.site.content.node_from_relative_path('jobs/')
		with Log("Checking jobs metadata") as l:
			for resource in jobs.walk_resources():
				if not resource.is_processable:
					l.output("Skipping %s" % (resource.name, ))
					continue
				with Log(resource.name):
					meta = resource.meta.to_dict()
					for tester in self._get_testers():
						assert tester.__doc__ is not None
						with Log("Test %s" % (tester.__doc__)):
							tester(resource)