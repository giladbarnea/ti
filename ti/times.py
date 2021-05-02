import re
from datetime import datetime, timedelta

from dateparser import parse as parsedate

from ti.error import BadTime

ABBREVS = {
    's': 'seconds',
    'm': 'minutes',
    'h': 'hours',
    'd': 'days',
    'w': 'weeks',
    'M': 'months'
    }


def reformat(date: str, fmt="%x %X") -> str:
    return formatted2dt(date).strftime(fmt)


def human2formatted(engtime: str = "now", fmt="%x %X") -> str:
    """Called by parse_args(), written as 'start' and 'end' values

    >>> human2formatted("yesterday")
    '04/26/21 17:16:54'
    """
    timediff: datetime = human2dt(engtime)
    return timediff.strftime(fmt)


def human2dt(engtime: str = "now") -> datetime:
    """
    Format is e.g.::

        <number>[ ?]<unit>[ ago]

    unit::

        s[ec[ond[s]]], m[in[ute[s]]], h[[ou]r[s]]

    For example: "1s ago", "2 minutes ago", "3hr"

    Returns:
        datetime: The difference between now and `engtime`.
    """

    match = re.match(r'(\d+)\s*([smhdwM])(\s+ago\s*)?$', engtime)
    if match is None:
        parsed = parsedate(engtime)
        if not parsed:
            raise BadTime(f"human2dt({engtime = })")
        return parsed
    now: datetime = datetime.now()
    amount = int(match.group(1))
    unit = match.group(2)

    parsed = now - timedelta(**{ABBREVS[unit]: amount})
    return parsed




    if not engtime or engtime.lower().strip() == 'now':
        return now

    match = re.match(r'(\d+)\s*(m|mins?|minutes?)(\s+ago\s*)?$', engtime, re.X)
    if match is not None:
        minutes = int(match.group(1))
        return now - timedelta(minutes=minutes)

    match = re.match(r'(\d+)\s*(h|hrs?|hours?)(\s+ago\s*)?$', engtime, re.X)
    if match is not None:
        hours = int(match.group(1))
        return now - timedelta(hours=hours)

    raise BadTime(f"Don't understand the time {engtime!r}")


def formatted2dt(date: str) -> datetime:
    """Called by log() and status() with 'start' and 'end' values.

    >>> formatted2dt('04/19/21 10:13:11')
    datetime(2021, 4, 19, 10, 13, 11)

    >>> formatted2dt('04/19/21')
    datetime.datetime(2021, 4, 19, 0, 0)

    >>> formatted2dt('10:13:11')
    datetime.datetime(2021, 4, 27, 10, 13, 11)
    """
    if ' ' in date:
        # "04/19/21 10:13:11" → datetime(...)
        return datetime.strptime(date, '%x %X')
    if '/' in date:
        # "04/19/21" → datetime(...)
        return datetime.strptime(date, '%x')
    # "10:13:11" → datetime(...)
    today = datetime.today()
    dt = datetime(today.year, today.month, today.day, *map(int, date.split(':')))
    return dt


def secs2human(secs: int) -> str:
    strings = []
    if secs > 3600:
        hours = int(secs // 3600)
        secs -= hours * 3600
        strings.append(str(hours) + ' hour' + ('s' if hours > 1 else ''))

    if secs > 60:
        mins = int(secs // 60)
        secs -= mins * 60
        strings.append(str(mins) + ' minute' + ('s' if mins > 1 else ''))

    if secs:
        strings.append(str(secs) + ' second' + ('s' if secs > 1 else ''))

    pretty = ', '.join(strings)[::-1].replace(',', '& ', 1)[::-1]
    return pretty


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
