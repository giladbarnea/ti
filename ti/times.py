import re
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Union

import arrow
from arrow import Arrow
from arrow.locales import EnglishLocale

from ti.config import config

# from dateparser import parse as _parsedate
# from functools import partial

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

# {'fri', 'friday', ...}
DAYS = set(map(str.lower, EnglishLocale.day_abbreviations[1:] + EnglishLocale.day_names[1:]))

# [(1, 'monday'), ..., (7, 'sunday')]
NUM2DAY = list(enumerate(map(str.lower, EnglishLocale.day_names[1:]), start=1))
TIMEUNIT_REMAINDER = "(?:ec(?:ond)?|in(ute)?|(ou)?r|ay|week)?s?"
HUMAN_RELATIVE = re.compile((rf'(?P<amount1>\d+)\s*(?P<unit1>([smhdw]))\s*{TIMEUNIT_REMAINDER}\s*'
                             rf'((?P<amount2>\d+)\s*(?P<unit2>([smhdw]))\s*{TIMEUNIT_REMAINDER}\s*'
                             rf'((?P<amount3>\d+)\s*(?P<unit3>([smhdw]))\s*{TIMEUNIT_REMAINDER})?)?\s*'
                             r'(?:\s+ago\s*)?$'), re.IGNORECASE)


def now() -> Arrow:
    return arrow.now(TZINFO)


def isoweekday(day: str) -> int:  # perf: µs
    """
    >>> isoweekday('mon') == 1
    >>> isoweekday('f') == 5
    """
    day = day.lower()
    if len(day) == 1 and day in ('t','s'):
        raise ValueError(f"ambiguous day: {repr(day)} (tuesday/thursday, saturday/sunday)")
    for num, day_name in NUM2DAY:
        if day_name.startswith(day):
            return num
    raise ValueError(f"unknown day: {repr(day)}")


def _day2arrow(day: str) -> Arrow:  # perf: µs
    """
    >>> _day2arrow('thurs')
    <Arrow ...>
    """
    _now = now()
    now_isoweekday = _now.isoweekday()
    day_isoweekday = isoweekday(day)
    diff = abs(now_isoweekday - day_isoweekday)
    if now_isoweekday <= day_isoweekday:
        shift = diff - 7
    else:
        shift = diff * -1
    return _now.shift(days=shift)


def reformat(date: Union[str, Arrow], fmt=DT_FMT) -> str:
    return formatted2arrow(date).format(fmt)


def human2formatted(engtime: str = "now", fmt=DT_FMT) -> str:
    """Called by parse_args(), written as 'start' and 'end' values

    >>> human2formatted("yesterday")
    '04/26/21 17:16:54'
    """
    arrw: Arrow = human2arrow(engtime)
    return arrw.format(fmt)


def _time2replace_dict(time: str) -> dict:
    """
    >>> _time2replace_dict('09:45')
    {'hour': 9, 'minute': 45}
    """
    match = re.match(r'(\d{1,2})(?::(\d{2}))?', time)
    if not match:
        raise ValueError(f"Don't understand {time = }")

    hours = int(match.group(1))
    minutes = match.group(2)
    replace = {'hour': hours}
    if minutes is not None:
        replace.update({'minute': int(minutes)})
    return replace


def _abs_time2arrow(time: str) -> Arrow:
    """
    >>> _abs_time2arrow('09:45')
    <Arrow ...>
    """
    replace = _time2replace_dict(time)
    return now().replace(**replace)


def _rel_time2arrow(time: str) -> Arrow:
    """
    >>> _rel_time2arrow('3m ago')
    <Arrow ...>
    """
    match = HUMAN_RELATIVE.fullmatch(time)
    if not match:
        raise ValueError(f"Don't understand {time = }")
    grpdict = match.groupdict()
    amount1 = int(grpdict['amount1'])
    unit1 = grpdict['unit1']
    delta = {ABBREVS[unit1]: amount1}
    if amount2 := grpdict.get('amount2'):
        delta.update({ABBREVS[grpdict['unit2']]: int(amount2)})
        if amount3 := grpdict.get('amount3'):
            delta.update({ABBREVS[grpdict['unit3']]: int(amount3)})
    parsed: Arrow = now() - timedelta(**delta)
    return parsed


def arrows2rel_time(late: Arrow, early: Arrow) -> str:
    """
    >>> arrows2rel_time(now(), now().shift(days=-5, minutes=3))
    '4 days, 23 hours & 57 minutes ago'
    """
    if (late.year != early.year or
            late.month != early.month):
        raise NotImplemented(f"Can only handle differences in weeks and below")
    secs = int((late - early).total_seconds())
    if not secs:
        return ''
    return secs2human(secs) + ' ago'


def human2arrow(engtime: Union[str, Arrow] = "now") -> Arrow:
    """
    Format is e.g.::

        <number>[ ?]<unit>[ ago]

    unit::

        s[ec[ond[s]]], m[in[ute[s]]], h[[ou]r[s]]

    For example: "1s ago", "2 minutes ago", "3hr"

    Returns:
        datetime: The difference between now and `engtime`.
    """
    if isinstance(engtime, Arrow):
        return engtime
    engtime = engtime.lower()

    # 'now', 'today', 'yesterday'
    if engtime in ('now', 'today'):
        return now()
    if engtime == 'yesterday':
        return now().shift(days=-1)

    # 'thurs', ...
    with suppress(ValueError):
        return _day2arrow(engtime)

    # '3m'
    with suppress(ValueError):
        return _rel_time2arrow(engtime)

    # '09:45'
    with suppress(ValueError):
        return _abs_time2arrow(engtime)

    # 'Wednesday 09:45'
    day, _, time = engtime.partition(' ')
    day = _day2arrow(day)
    replace = _time2replace_dict(time)
    return day.replace(**replace)

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


def formatted2arrow(date: Union[str, Arrow]) -> Arrow:
    """Called by log() and status() with 'start' and 'end' values.

    >>> formatted2arrow('04/19/21 10:13:11')
    datetime(2021, 4, 19, 10, 13, 11)

    >>> formatted2arrow('04/19/21')
    datetime.datetime(2021, 4, 19, 0, 0)

    >>> formatted2arrow('10:13:11')
    datetime.datetime(2021, 4, 27, 10, 13, 11)
    """
    if isinstance(date, Arrow):
        return date
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
    """
    >>> secs2human(777600)
    '1 week & 2 days'

    >>> secs2human(7201)
    '2 hours & 1 second'
    """
    strings = []
    if secs >= 604800:
        weeks = int(secs // 604800)
        secs -= weeks * 604800
        strings.append(str(weeks) + ' week' + ('s' if weeks > 1 else ''))

    if secs >= 86400:
        days = int(secs // 86400)
        secs -= days * 86400
        strings.append(str(days) + ' day' + ('s' if days > 1 else ''))

    if secs >= 3600:
        hours = int(secs // 3600)
        secs -= hours * 3600
        strings.append(str(hours) + ' hour' + ('s' if hours > 1 else ''))

    if secs >= 60:
        mins = int(secs // 60)
        secs -= mins * 60
        strings.append(str(mins) + ' minute' + ('s' if mins > 1 else ''))

    if secs:
        strings.append(str(secs) + ' second' + ('s' if secs > 1 else ''))

    human = ', '.join(strings)[::-1].replace(',', '& ', 1)[::-1]
    return human


def timegap(start_time: Arrow, end_time: Arrow) -> str:
    # TODO: this is the same as arrows2rel_time
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
