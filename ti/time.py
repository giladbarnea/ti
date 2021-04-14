from datetime import datetime, timedelta
import re
from ti.error import BadTime

def to_datetime(timestr):
	return parse_engtime(timestr).isoformat() + 'Z'


def parse_engtime(timestr="") -> datetime:
	"""
	Format is e.g.::

		<number>[ ?]<unit>[ ago]

	unit::

		s[ec[ond[s]]], m[in[ute[s]]], h[[ou]r[s]]

	For example: "1s ago", "2 minutes ago", "3hr"

	Returns:
		datetime: The difference between now and `timestr`.
	"""
	now: datetime = datetime.utcnow()
	if not timestr or timestr.strip() == 'now':
		return now

	match = re.match(r'(\d+|a)\s*(s|secs?|seconds?)( \s+ ago\s*)?$',
					 timestr, re.X)
	if match is not None:
		n = match.group(1)
		seconds = 1 if n == 'a' else int(n)
		return now - timedelta(seconds=seconds)

	match = re.match(r'(\d+|a)\s*(m|mins?|minutes?)( \s+ ago\s*)?$', timestr, re.X)
	if match is not None:
		n = match.group(1)
		minutes = 1 if n == 'a' else int(n)
		return now - timedelta(minutes=minutes)

	match = re.match(r'(\d+|a|an)\s*(h|hrs?|hours?)( \s+ ago\s*)?$', timestr, re.X)
	if match is not None:
		n = match.group(1)
		hours = 1 if n in ['a', 'an'] else int(n)
		return now - timedelta(hours=hours)

	raise BadTime("Don't understand the time %r" % (timestr,))


def parse_isotime(isotime):
	return datetime.strptime(isotime, '%Y-%m-%dT%H:%M:%S.%fZ')


def timegap(start_time, end_time):
	diff = end_time - start_time

	mins = diff.total_seconds() // 60

	if mins == 0:
		return 'less than a minute'
	elif mins == 1:
		return 'a minute'
	elif mins < 44:
		return '{} minutes'.format(mins)
	elif mins < 89:
		return 'about an hour'
	elif mins < 1439:
		return 'about {} hours'.format(mins // 60)
	elif mins < 2519:
		return 'about a day'
	elif mins < 43199:
		return 'about {} days'.format(mins // 1440)
	elif mins < 86399:
		return 'about a month'
	elif mins < 525599:
		return 'about {} months'.format(mins // 43200)
	else:
		return 'more than a year'