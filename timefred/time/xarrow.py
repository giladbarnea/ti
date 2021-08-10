import re
from contextlib import suppress
from datetime import datetime, timedelta, tzinfo as dt_tzinfo
from typing import Type, Optional, Any, Union

from arrow import Arrow, ArrowFactory
from arrow.arrow import TZ_EXPR

import timefred.color as c
from timefred.config import config
from timefred.time.timeutils import isoweekday
from timefred.util import confirm

FORMATS = config.time.formats
TZINFO = config.time.tz

ABBREVS = {
    's': 'seconds',
    'm': 'minutes',
    'h': 'hours',
    'd': 'days',
    'w': 'weeks',
    'M': 'months'
    }

# DAYS = set(map(str.lower, EnglishLocale.day_abbreviations[1:] + EnglishLocale.day_names[1:]))
# """{'fri', 'friday', ...}"""

TIMEUNIT_REMAINDER = "(?:ec(?:ond)?|in(ute)?|(ou)?r|ay|eek|onth)?s?"

HUMAN_RELATIVE = re.compile((rf'(?P<amount1>\d+)\s*(?P<fullunit1>(?P<unit1>([smhdw]))\s*{TIMEUNIT_REMAINDER})\s*'
                             rf'('
                             rf'(?P<amount2>\d+)\s*(?P<fullunit2>(?P<unit2>([smhdw]))\s*{TIMEUNIT_REMAINDER})\s*'
                             rf'('
                             rf'(?P<amount3>\d+)\s*(?P<fullunit3>(?P<unit3>([smhdw]))\s*{TIMEUNIT_REMAINDER})'
                             rf')?'
                             rf')?'
                             rf'\s*'
                             r'(?:\s+ago\s*)?$'), re.IGNORECASE)
"""3 hours 2m 15 secs ago
Used in `XArrow._from_relative`"""


class XArrow(Arrow):
    def __init__(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0, tzinfo: Optional[TZ_EXPR] = None, **kwargs: Any) -> None:
        super().__init__(year, month, day, hour, minute, second, microsecond, tzinfo, **kwargs)
        self.colored = c.time(self)
        self._HHmmss = None
        self._DDMMYY = None
        self._DDMMYYHHmmss = None
        self._full = None

    @classmethod
    # @break_on_return(condition=lambda rv:not isinstance(rv, XArrow))
    def now(cls, tzinfo: Optional[dt_tzinfo] = None) -> "XArrow":
        return super().now(tzinfo)
        # return xarrow_factory.now(TZINFO)

    @classmethod
    def from_formatted(cls, date: Union[str, 'XArrow']) -> 'XArrow':
        if isinstance(date, Arrow):
            if not isinstance(date, XArrow) \
                    and confirm(f'XArrow.from_formatted({date = }) is regular Arrow, debug?'):
                breakpoint()
            return date

        # noinspection PyTypeChecker
        return xarrow_factory.get(date, [f"{FORMATS.date} HH:mm:ss",
                                         f"{FORMATS.date} HH:mm",
                                         f"{FORMATS.date}",
                                         f"{FORMATS.short_date}",
                                         "HH:mm:ss",
                                         "HH:mm",
                                         ],
                                  tzinfo=TZINFO)

        if ' ' in date:
            # "19/04/21 10:13:11" → arrow(...)
            # return xarrow_factory.get(date, FORMATS.date_time, tzinfo=TZINFO)
            return xarrow_factory.get(date, ["DD/MM/YY HH:mm:ss",
                                             "DD/MM/YY HH:mm"], tzinfo=TZINFO)
        if '/' in date:
            # "19/04/21" → arrow(...)
            if date.count('/') == 1:
                # "19/04"
                date += '/' + str(datetime.today().year)[-2:]
            return xarrow_factory.get(date, FORMATS.date, tzinfo=TZINFO)

        # "10:13:11" → datetime(...)
        today = datetime.today()
        return cls(today.year, today.month, today.day, *map(int, date.split(':')))

    @classmethod
    def _from_day(cls, day: str) -> 'XArrow':  # perf: µs
        """
        >>> XArrow._from_day('thurs')
        <XArrow ...>
        """
        now = cls.now()
        now_isoweekday = now.isoweekday()
        day_isoweekday = isoweekday(day)
        diff = abs(now_isoweekday - day_isoweekday)
        if now_isoweekday <= day_isoweekday:
            shift = diff - 7
        else:
            shift = diff * -1
        return now.shift(days=shift)

    @classmethod
    def _from_relative(cls, time: str) -> 'XArrow':
        """
        >>> XArrow._from_relative('3m ago')
        <XArrow ...>
        """
        match = HUMAN_RELATIVE.fullmatch(time)
        if not match:
            raise ValueError(f"Don't understand {time = }")
        grpdict = match.groupdict()
        amount1 = int(grpdict['amount1'])
        unit1 = grpdict['unit1']
        fullunit1 = grpdict['fullunit1']
        if unit1 == 'm' and fullunit1 == 'month':
            unit1 = 'M'
        delta = {ABBREVS[unit1]: amount1}
        if amount2 := grpdict.get('amount2'):
            delta.update({ABBREVS[grpdict['unit2']]: int(amount2)})
            if amount3 := grpdict.get('amount3'):
                delta.update({ABBREVS[grpdict['unit3']]: int(amount3)})
        parsed: XArrow = cls.now() - timedelta(**delta)
        return parsed

    @classmethod
    def _from_absolute(cls, time: str) -> 'XArrow':
        """
        >>> XArrow._from_absolute('09:45')
        <XArrow ...>
        """
        # replace = _time2replace_dict(time)
        return cls.now().update(time)

    @classmethod
    def from_human(cls, engtime: Union[str, 'XArrow'] = "now") -> 'XArrow':
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
            if not isinstance(engtime, XArrow) \
                    and confirm(f'XArrow.from_human({engtime = }) is regular Arrow, debug?'):
                breakpoint()
            return engtime
        engtime = engtime.lower()

        # 'now', 'today', 'yesterday'
        if engtime in ('now', 'today'):
            return cls.now()
        if engtime == 'yesterday':
            return cls.now().shift(days=-1)

        # 'thurs', ...
        with suppress(ValueError):
            return cls._from_day(engtime)

        # '3m'
        with suppress(ValueError):
            return cls._from_relative(engtime)

        # '09:45'
        with suppress(ValueError):
            return XArrow._from_absolute(engtime)

        # 05/18/21
        if '/' in engtime:
            return XArrow.from_formatted(engtime)

        # 'Wednesday 09:45'
        day, _, time = engtime.partition(' ')
        # TODO: '05/20/21' doesnt work! and enters here
        day = cls._from_day(day)
        # replace = _time2replace_dict(time)
        return day.update(time)

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

    def update(self, time) -> 'XArrow':
        """
        >>> self.replace('09:45')
        {'hour': 9, 'minute': 45}
        """
        if '/' in time:
            raise ValueError(f"Don't understand {time = }")
        match = re.match(r'(\d{1,2})(?::(\d{2})(?::(\d{2}))?)?', time)
        if not match:
            raise ValueError(f"Don't understand {time = }")

        hours = int(match.group(1))
        minutes = match.group(2)
        replace = {'hour': hours}
        if minutes is not None:
            replace.update({'minute': int(minutes)})
        else:
            replace.update({'minute': 0})
        seconds = match.group(3)
        if seconds is not None:
            replace.update({'second': int(seconds)})
        else:
            replace.update({'second': 0})
        return self.replace(**replace)

    @property
    def HHmmss(self):
        if not self._HHmmss:
            self._HHmmss: str = self.format(FORMATS.time)
        return self._HHmmss

    @property
    def DDMMYY(self):
        if not self._DDMMYY:
            self._DDMMYY: str = self.format(FORMATS.date)
        return self._DDMMYY

    @property
    def DDMMYYHHmmss(self):
        if not self._DDMMYYHHmmss:
            self._DDMMYYHHmmss: str = self.format(f'{FORMATS.date} {FORMATS.time}')
        return self._DDMMYYHHmmss

    @property
    def full(self):
        """'Thursday 20/05/21'"""
        if not self._full:
            self._full: str = f"{self.strftime('%A')} {self.DDMMYY}"
        return self._full


class XArrowFactory(ArrowFactory):
    type: Type[XArrow]

    def __init__(self, type: Type[XArrow] = XArrow) -> None:
        super().__init__(type)


xarrow_factory = XArrowFactory()
