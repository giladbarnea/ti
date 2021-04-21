from datetime import datetime, timedelta
from dateparser import parse as parsedate

from loguru import logger
import re
from ti.error import BadTime

@logger.catch()
def to_human(engtime=""):
	"""Called by parse_args(), written as 'start' and 'end' values"""
	timediff: datetime = parse_engtime(engtime)
	return timediff.strftime('%x %X')


def parse_engtime(engtime="") -> datetime:
	"""
	Format is e.g.::

		<number>[ ?]<unit>[ ago]

	unit::

		s[ec[ond[s]]], m[in[ute[s]]], h[[ou]r[s]]

	For example: "1s ago", "2 minutes ago", "3hr"

	Returns:
		datetime: The difference between now and `engtime`.
	"""
	if not engtime:
		return parsedate('now')
	return parsedate(engtime)
	now: datetime = datetime.now()
	if not engtime or engtime.lower().strip() == 'now':
		return now
	# parsed = parse(engtime)
	# td = now - parsed
	match = re.match(r'(\d+)\s*(s|secs?|seconds?)(\s+ago\s*)?$', engtime, re.X)
	if match is not None:
		seconds = int(match.group(1))
		return now - timedelta(seconds=seconds)

	match = re.match(r'(\d+)\s*(m|mins?|minutes?)(\s+ago\s*)?$', engtime, re.X)
	if match is not None:
		minutes = int(match.group(1))
		return now - timedelta(minutes=minutes)

	match = re.match(r'(\d+)\s*(h|hrs?|hours?)(\s+ago\s*)?$', engtime, re.X)
	if match is not None:
		hours = int(match.group(1))
		return now - timedelta(hours=hours)

	raise BadTime(f"Don't understand the time {engtime!r}")


def parse_human(isotime) -> datetime:
	"""Called by action_log() and action_status() with 'start' and 'end' values ('04/19/21 10:13:11')"""
	return datetime.strptime(isotime, '%x %X')


def timegap(start_time, end_time):
	diff = end_time - start_time

	mins = int(diff.total_seconds() // 60)

	if mins == 0:
		return 'less than a minute'
	elif mins == 1:
		return 'a minute'
	elif mins < 44:
		return f'{mins} minutes'
	elif mins < 89:
		return 'about an hour'
	elif mins < 1439:
		hours = int(mins // 60)
		mins_remainder = int(mins % 60)
		return f'about {hours} hours and {mins_remainder} minutes'
	elif mins < 2519:
		return 'about a day'
	elif mins < 43199:
		return f'about {mins // 1440} days'
	elif mins < 86399:
		return 'about a month'
	elif mins < 525599:
		return f'about {mins // 43200} months'
	else:
		return 'more than a year'