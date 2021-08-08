from arrow.locales import EnglishLocale


NUM2DAY = list(enumerate(map(str.lower, EnglishLocale.day_names[1:]), start=1))
"""[(1, 'monday'), ..., (7, 'sunday')]"""

def isoweekday(day: str) -> int:  # perf: µs
    """
    >>> isoweekday('mon') == 1
    >>> isoweekday('f') == 5
    """
    day = day.lower()
    if len(day) == 1 and day in ('t', 's'):
        raise ValueError(f"ambiguous day: {repr(day)} (tuesday/thursday, saturday/sunday)")
    for num, day_name in NUM2DAY:
        if day_name.startswith(day):
            return num
    raise ValueError(f"unknown day: {repr(day)}")


def arrows2rel_time(late: "XArrow", early: "XArrow") -> str:
    """
    >>> arrows2rel_time(now(), now().shift(days=-5, minutes=3))
    '4 days, 23 hours & 57 minutes ago'
    """
    # if (late.year != early.year or
    #         late.month != early.month):
    #     raise NotImplemented(f"Can only handle differences in weeks and below")
    secs = int((late - early).total_seconds())
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
