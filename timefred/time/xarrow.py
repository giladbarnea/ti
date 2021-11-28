import re
from collections.abc import Callable
from contextlib import suppress
from datetime import timedelta, tzinfo as dt_tzinfo  # , date
# from time import struct_time
from typing import Type, Optional, Any, Union, Literal, overload, final

from arrow import Arrow, ArrowFactory
from arrow.arrow import TZ_EXPR
from arrow.locales import EnglishLocale

import timefred.color as c
from timefred.config import config
from timefred.time.timeutils import isoweekday


@final
class NoneType:
    def __bool__(self) -> Literal[False]: ...


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
Used in `XArrow._dehumanize_relative`"""

# EnglishLocale.timeframes |= {
#     "day":     "({0}|a) day",
#     # "d":     "({0}|a) day",
#     "minute":  "({0}|a) minutes",
#     "hour":    "({0}|a) hours",
#     "week":    "({0}|a) weeks",
#     "month":   "({0}|a) months",
#     "quarter": "({0}|a) quarters",
#     "year":    "({0}|a) years",
#     }


class XArrow(Arrow):
    def __init__(self,
                 year: int,
                 month: int,
                 day: int,
                 hour: int = 0,
                 minute: int = 0,
                 second: int = 0,
                 microsecond: int = 0,
                 tzinfo: Optional[TZ_EXPR] = None,
                 **kwargs: Any) -> None:
        self._HHmmss = None
        self._DDMMYY = None
        self._DDMMYYHHmmss = None
        self._full = None
        self._colored = None
        super().__init__(year, month, day, hour, minute, second, microsecond, tzinfo, **kwargs)
    
    @property
    def colored(self):
        if not self._colored:
            self._colored = c.time(str(self))
        return self._colored
    
    @classmethod
    def now(cls, tzinfo: Optional[dt_tzinfo] = None) -> "XArrow":
        rv = super().now(tzinfo)
        assert isinstance(rv, XArrow), f"{cls.__qualname__}.now({tzinfo = !r}) returning {rv = !r} (not XArrow)"
        return rv
    
    @classmethod
    def from_formatted(cls, date: Union[str, "XArrow"]) -> "XArrow":
        """`date` can be any `config.time.formats`, e.g `DD/MM/YY HH:mm:ss` ... `HH:MM`"""
        if isinstance(date, Arrow):
            if isinstance(date, XArrow):
                return date
            raise NotImplementedError(f"{cls.__qualname__}.from_formatted({date = !r}) is Arrow")
        
        return xarrow_factory.get(date, [FORMATS.datetime,  # DD/MM/YY HH:mm:ss
                                         FORMATS.shorter_datetime,  # DD/MM/YY HH:mm
                                         FORMATS.short_datetime,  # DD/MM HH:mm
                                         FORMATS.date,  # DD/MM/YY
                                         FORMATS.short_date,  # DD/MM
                                         FORMATS.time,  # HH:mm:ss
                                         FORMATS.short_time,  # HH:mm
                                         ],
                                  tzinfo=TZINFO)
    
    @classmethod
    def from_day(cls, day: Union[str, "XArrow"]) -> "XArrow":  # perf: µs
        """
        >>> XArrow.from_day('thurs')
        <XArrow ...>
        """
        now = cls.now()
        now_isoweekday: int = now.isoweekday()
        day_isoweekday: int = isoweekday(day)
        if now_isoweekday == day_isoweekday:
            return now
        diff = abs(now_isoweekday - day_isoweekday)
        if now_isoweekday < day_isoweekday:
            shift = diff - 7
        else:
            shift = diff * -1
        return now.shift(days=shift)
    
    @classmethod
    def _dehumanize_relative(cls, time: Union[str, "XArrow"]) -> "XArrow":
        """
        >>> XArrow._dehumanize_relative('3m ago')
        <XArrow ...>
        """
        match = HUMAN_RELATIVE.fullmatch(time)
        if not match:
            raise ValueError(f"Don't understand {time = !r}")
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
        if not isinstance(parsed, XArrow):
            raise NotImplementedError(f"{cls.__qualname__}._dehumanize_relative({time = !r}) returning {parsed = !r} (not XArrow)")
        return parsed
    
    @classmethod
    def from_absolute(cls, time: Union[str, "XArrow"]) -> "XArrow":
        """
        >>> XArrow.from_absolute('09:45')
        <XArrow ...>
        """
        return cls.now().update(time)
    
    # noinspection PyMethodOverriding,PyMethodParameters
    @overload
    def dehumanize(input_string: str, locale: str = "local") -> "XArrow":
        ...
    
    @overload
    def dehumanize(self: "XArrow", input_string: str, locale: str = "local") -> "XArrow":
        ...
    
    # noinspection PyMethodParameters
    def dehumanize(self_or_input_string, input_string_or_locale: str = None, locale: str = "local") -> "XArrow":
        if isinstance(self_or_input_string, str):
            called_static = True
            input_string = self_or_input_string.lower()
        else:
            called_static = False
            input_string = input_string_or_locale.lower()
        
        if input_string in ('now', 'today'):
            return XArrow.now()
        
        if input_string in ('yesterday', 'tomorrow'):
            return XArrow.now().shift(days=+1 if input_string == 'tomorrow' else -1)
        
        if called_static:
            self: XArrow = XArrow.now()
        else:
            self: XArrow = self_or_input_string
        rv = super(type(self), self).dehumanize(input_string)
        assert isinstance(rv, XArrow)
        return rv
    
    @classmethod
    def from_human(cls, human_time: Union[str, "XArrow"] = "now") -> "XArrow":
        """
        Format is e.g.::

            <number>[ ?]<unit>[ ago]

        unit::

            s[ec[ond[s]]], m[in[ute[s]]], h[[ou]r[s]]

        For example: "1s ago", "2 minutes ago", "3hr"
        """
        if isinstance(human_time, Arrow):
            if isinstance(human_time, XArrow):
                return human_time
            raise NotImplementedError(f"{cls.__qualname__}.from_human({human_time = !r}) is Arrow")
        human_time = human_time.lower()
        
        # 'now', 'today', 'yesterday'
        if human_time in ('now', 'today'):
            return cls.now()
        if human_time == 'yesterday':
            return cls.now().shift(days=-1)
        
        # 'thurs', ...
        with suppress(ValueError):
            return cls.from_day(human_time)
        
        # '3m'
        with suppress(ValueError):
            return cls._dehumanize_relative(human_time)
        
        # '09:45'
        with suppress(ValueError):
            return cls.from_absolute(human_time)
        
        # 05/18/21
        if FORMATS.date_separator in human_time:
            return cls.from_formatted(human_time)
        
        # 'Wednesday 09:45'
        day, _, time = human_time.partition(' ')
        # TODO: '05/20/21' doesnt work! and enters here
        day = cls.from_day(day)
        return day.update(time)
        
        #
        # parsed = parsedate(human_time)
        #
        #
        # if not parsed:
        #     raise BadTime(f"BadTime: human2dt({human_time = })")
        # return parsed
        # if not human_time or human_time.lower().strip() == 'now':
        #     return now
        #
        # match = re.match(r'(\d+)\s*(m|mins?|minutes?)(\s+ago\s*)?$', human_time, re.X)
        # if match is not None:
        #     minutes = int(match.group(1))
        #     return now - timedelta(minutes=minutes)
        #
        # match = re.match(r'(\d+)\s*(h|hrs?|hours?)(\s+ago\s*)?$', human_time, re.X)
        # if match is not None:
        #     hours = int(match.group(1))
        #     return now - timedelta(hours=hours)
        #
        # raise BadTime(f"Don't understand the time {human_time!r}")
    
    def update(self, time: Union[str, "XArrow"]) -> "XArrow":
        """
        >>> self.update('09:45')
        <XArrow ...>
        """
        if isinstance(time, XArrow):
            return time
        if FORMATS.date_separator in time:
            raise NotImplementedError(f"Looks like {time = !r} is a date. Currently can only update time.")
        time_match = FORMATS.time_format_re.match(time)
        if not time_match:
            raise ValueError(f"{time = !r} doesn't match {FORMATS.time_format_re}")
        
        time_match_dict = time_match.groupdict()
        replace = {}
        if (hour := time_match_dict['hour']) is not None:
            replace['hour'] = int(hour)
        if (minute := time_match_dict['minute']) is not None:
            replace['minute'] = int(minute)
        if (second := time_match_dict['second']) is not None:
            replace['second'] = int(second)
        
        rv = self.replace(**replace)
        return rv
    
    @overload
    def isoweekday(self, human: NoneType = None) -> int:
        ...
    
    @overload
    def isoweekday(self, human: Literal['short'] = 'short') -> str:
        ...
    
    @overload
    def isoweekday(self, human: Literal['full'] = 'full') -> str:
        ...
    
    def isoweekday(self, human=None):
        """"""
        if not human:
            return isoweekday(self.strftime('%a'))
        if human == 'short':
            return self.strftime('%a')
        if human == 'full':
            return self.strftime('%A')
        raise ValueError(f"Bad 'human' value, can be either 'short' or 'full'. Got XArrow.isoweekday({human = !r})")
    
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
        """'28/10/21 08:20:00'"""
        if not self._DDMMYYHHmmss:
            self._DDMMYYHHmmss: str = self.format(f'{FORMATS.date} {FORMATS.time}')
        return self._DDMMYYHHmmss
    
    @property
    def full(self):
        """'Thursday 20/05/21 08:20:00'"""
        if not self._full:
            self._full: str = f"{self.isoweekday('full')} {self.DDMMYYHHmmss}"
        return self._full
    
    def __str__(self):
        return self.DDMMYYHHmmss
    
    def __repr__(self):
        return f'{self.__class__.__qualname__} ⟨{self.DDMMYYHHmmss}⟩'


class XArrowFactory(ArrowFactory):
    type: Type[XArrow]
    
    def __init__(self, type: Type[XArrow] = XArrow) -> None:
        super().__init__(type)
    
    get: Callable[..., XArrow]


# Docs say factory = arrow.ArrowFactory(XArrow)
# https://arrow.readthedocs.io/en/latest/#factories
xarrow_factory = XArrowFactory()