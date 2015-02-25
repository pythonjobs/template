import hyde.plugin
import datetime
import re
from fin.contextlog import Log

class CheckMetaPlugin(hyde.plugin.Plugin):

	REQUIRED_META = {
		'title': re.compile('.{5,}'),
		'company': re.compile('.{3,}'),
		'email': re.compile('^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,10}$', re.I),
		'created': lambda x: isinstance(x, (datetime.date, datetime.datetime))
	}

	def begin_site(self):
		jobs = self.site.content.node_from_relative_path('jobs/')
		with Log("Checking jobs metadata") as l:
			for resource in jobs.walk_resources():
				if not resource.is_processable:
					l.output("Skipping %s" % (resource.name, ))
					continue
				with Log(resource.name):
					meta = resource.meta.to_dict()
					for key, check in self.REQUIRED_META.iteritems():
						if callable(check):
							if not check(meta.get(key)):
								raise RuntimeError("Job %s frontmatter '%s' has not been accepted" % (resource.name, key))	
						else:
							if not key in meta:
								raise RuntimeError("Job %s must specify '%s' in frontmatter" % (resource.name, key))
							if not check.match(meta[key]):
								raise RuntimeError("Job %s has invalid '%s' in frontmatter: '%s'" % (resource.name, key, meta[key]))

