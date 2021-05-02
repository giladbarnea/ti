import re
from contextlib import suppress
from datetime import datetime, timedelta

import arrow
from arrow import Arrow
from arrow.locales import EnglishLocale

# from dateparser import parse as _parsedate
# from functools import partial

from ti.config import config

if config:
    # parsedate = partial(_parsedate, settings={'TIMEZONE': config.time.tz, 'RETURN_AS_TIMEZONE_AWARE': True})
    TZINFO = config.time.tz
    FMT = config.time.format
    DT_FMT = FMT + f" HH:mm:ss"
    # dtnow = partial(datetime.now, TZINFO)
else:
    # parsedate = _parsedate
    TZINFO = None
    FMT = 'MM/DD/YY'
    DT_FMT = FMT + f" HH:mm:ss"
    # dtnow = datetime.now

ABBREVS = {
    's': 'seconds',
    'm': 'minutes',
    'h': 'hours',
    'd': 'days',
    'w': 'weeks',
    'M': 'months'
    }

DAYS = set(map(str.lower, EnglishLocale.day_abbreviations[1:] + EnglishLocale.day_names[1:]))


def now() -> Arrow:
    return arrow.now(TZINFO)


def day_num(day: str) -> int:
    day = day.lower()
    for num, day_name in enumerate(map(str.lower, EnglishLocale.day_names[1:]), start=1):
        if day_name.startswith(day):
            return num
    raise ValueError(f"unknown day: {repr(day)}")


def day2arrow(day: str) -> Arrow:
    return now().shift(days=-1 * (7 - day_num(day)))


def reformat(date: str, fmt=DT_FMT) -> str:
    return formatted2arrow(date).strftime(fmt)


def human2formatted(engtime: str = "now", fmt=DT_FMT) -> str:
    """Called by parse_args(), written as 'start' and 'end' values

    >>> human2formatted("yesterday")
    '04/26/21 17:16:54'
    """
    arrw: Arrow = human2arrow(engtime)
    return arrw.format(fmt)


def human2arrow(engtime: str = "now") -> Arrow:
    """
    Format is e.g.::

        <number>[ ?]<unit>[ ago]

    unit::

        s[ec[ond[s]]], m[in[ute[s]]], h[[ou]r[s]]

    For example: "1s ago", "2 minutes ago", "3hr"

    Returns:
        datetime: The difference between now and `engtime`.
    """
    engtime = engtime.lower()
    if engtime in ('now', 'today'):
        return now()
    if engtime == 'yesterday':
        return now().shift(days=-1)

    with suppress(ValueError):
        return day2arrow(engtime)

    TIMEUNIT_REMAINDER = "(?:ec(?:ond)?|in(ute)?|(ou)?r|ay|week)?s?"
    match = re.fullmatch((rf'(?P<amount1>\d+)\s*(?P<unit1>([smhdw]))\s*{TIMEUNIT_REMAINDER}\s*'
                          rf'((?P<amount2>\d+)\s*(?P<unit2>([smhdw]))\s*{TIMEUNIT_REMAINDER}\s*'
                          rf'((?P<amount3>\d+)\s*(?P<unit3>([smhdw]))\s*{TIMEUNIT_REMAINDER})?)?\s*'
                          r'(?:\s+ago\s*)?$'), engtime, re.IGNORECASE)
    if match:
        # 3m ago
        grpdict = match.groupdict()
        amount1 = int(grpdict['amount1'])
        unit1 = grpdict['unit1']
        delta = {ABBREVS[unit1]: amount1}
        if amount2 := grpdict.get('amount2'):
            delta.update({ABBREVS[grpdict['unit2']]: int(amount2)})
            if amount3 := grpdict.get('amount3'):
                delta.update({ABBREVS[grpdict['unit3']]: int(amount3)})
        parsed = now() - timedelta(**delta)
        return parsed

    match = re.match(r'(\d{1,2})(?::(\d{2}))?', engtime)
    if match:
        hours = int(match.group(1))
        minutes = match.group(2)
        replace = {'hour': hours}
        if minutes is not None:
            replace.update({'minute': int(minutes)})

        return now().replace(**replace)

    #
    # parsed = parsedate(engtime)
    #
    #
    # if not parsed:
    #     raise BadTime(f"BadTime: human2dt({engtime = })")
    # return parsed
    # if not engtime or engtime.lower().strip() == 'now':
    #     return now
    #
    # match = re.match(r'(\d+)\s*(m|mins?|minutes?)(\s+ago\s*)?$', engtime, re.X)
    # if match is not None:
    #     minutes = int(match.group(1))
    #     return now - timedelta(minutes=minutes)
    #
    # match = re.match(r'(\d+)\s*(h|hrs?|hours?)(\s+ago\s*)?$', engtime, re.X)
    # if match is not None:
    #     hours = int(match.group(1))
    #     return now - timedelta(hours=hours)
    #
    # raise BadTime(f"Don't understand the time {engtime!r}")


def formatted2arrow(date: str) -> Arrow:
    """Called by log() and status() with 'start' and 'end' values.

    >>> formatted2arrow('04/19/21 10:13:11')
    datetime(2021, 4, 19, 10, 13, 11)

    >>> formatted2arrow('04/19/21')
    datetime.datetime(2021, 4, 19, 0, 0)

    >>> formatted2arrow('10:13:11')
    datetime.datetime(2021, 4, 27, 10, 13, 11)
    """
    if ' ' in date:
        # "04/19/21 10:13:11" → arrow(...)
        return arrow.get(date, DT_FMT, tzinfo=TZINFO)
        # return datetime.strptime(date, DT_FMT).astimezone(TZINFO)
    if '/' in date:
        # "04/19/21" → arrow(...)
        return arrow.get(date, FMT, tzinfo=TZINFO)
        # return datetime.strptime(date, DT_FMT).astimezone(TZINFO)
    # "10:13:11" → datetime(...)
    today = datetime.today()
    return arrow.Arrow(today.year, today.month, today.day, *map(int, date.split(':')))
    # return dt


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


def timegap(start_time: Arrow, end_time: Arrow) -> str:
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
