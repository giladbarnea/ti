from arrow.locales import EnglishLocale

from timefred.log import log
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
    # if (present.year != past.year or
    #         present.month != past.month):
    #     raise NotImplemented(f"Can only handle differences in weeks and below")
    secs = int((present - past).total_seconds())
    if not secs:
        return ''
    ret = secs2human(secs) + ' ago'
    # log.debug(f'arrows2rel_time({present = }, {past = })',
    #           f'{secs = }',
    #           f'  -> {ret}')
    return ret


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
    if secs >= 3600 * 24 * 7 * 52:
        years = int(secs // (3600 * 24 * 7 * 52))
        secs -= years * 3600 * 24 * 7 * 52
        strings.append(str(years) + ' year' + ('s' if years > 1 else ''))
    
    if secs >= 3600 * 24 * 7 * 4:
        months = int(secs // (3600 * 24 * 7 * 4))
        secs -= months * 3600 * 24 * 7 * 4
        strings.append(str(months) + ' month' + ('s' if months > 1 else ''))
    
    if secs >= 3600 * 24 * 7:
        weeks = int(secs // (3600 * 24 * 7))
        secs -= weeks * 3600 * 24 * 7
        strings.append(str(weeks) + ' week' + ('s' if weeks > 1 else ''))

    if secs >= 3600 * 24:
        days = int(secs // (3600 * 24))
        secs -= days * 3600 * 24
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
