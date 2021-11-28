from arrow.locales import EnglishLocale

from timefred.config import config

if config.time.first_day_of_week == 'monday':
    NUM2DAY = list(enumerate(map(str.lower, EnglishLocale.day_names[1:]), start=1))
    """[(1, 'monday'), ..., (7, 'sunday')]"""
else:
    NUM2DAY = list(enumerate(map(str.lower, [EnglishLocale.day_names[-1]] + EnglishLocale.day_names[1:-1]), start=1))
    """[(1, 'sunday'), ..., (7, 'saturday')]"""

def isoweekday(day: str) -> int:  # perf: µs
    """
    Depending on config.time.first_day_of_week, returns the ISO week day number
    >>> isoweekday('mon') == 1 or isoweekday('mon') == 2
    >>> isoweekday('f') == ...
    >>> isoweekday('Saturday') == ...
    """
    day = day.lower()
    if len(day) == 1 and day in ('t', 's'):
        raise ValueError(f"Ambiguous day: {day!r} (tuesday/thursday, saturday/sunday)")
    for num, day_name in NUM2DAY:
        if day_name.startswith(day):
            return num
    raise ValueError(f"Unknown day: {day!r}")


def arrows2rel_time(present: "XArrow", past: "XArrow") -> str:
    """
    >>> arrows2rel_time(now(), now().shift(days=-5, minutes=3))
    '4 days, 23 hours & 57 minutes ago'
    """
    # TODO: check out present.humanize(past, granularity=["hour", "minute", "second"])
    # if (present.year != past.year or
    #         present.month != past.month):
    #     raise NotImplemented(f"Can only handle differences in weeks and below")
    secs = int((present - past).total_seconds())
    if not secs:
        return ''
    return secs2human(secs) + ' ago'


def secs2human(secs: int) -> str:
    """
    >>> secs2human(777600)
    '1 week & 2 days'

    >>> secs2human(7201)
    '2 hours & 1 second'
    """
    if not isinstance(secs, int):
        breakpoint()
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
