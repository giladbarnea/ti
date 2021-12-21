import re
from collections.abc import Callable
from contextlib import suppress
from datetime import tzinfo as dt_tzinfo, time as dt_time
# from time import struct_time
from typing import Type, Optional, Any, Union, Literal, overload, final

from arrow import Arrow, ArrowFactory
from arrow.arrow import TZ_EXPR
# from dateutil.relativedelta import relativedelta

import timefred.color as c
from timefred.config import config
from timefred.time.timeutils import isoweekday


@final
class NoneType:
    def __bool__(self) -> Literal[False]: ...


FORMATS = config.time.formats
TZINFO = config.time.tz

TIME_UNITS_FIRST_DIGIT_TO_PLURAL = {
    's': 'seconds',
    'm': 'minutes',
    'h': 'hours',
    'd': 'days',
    'w': 'weeks',
    'M': 'months',
    'q': 'quarters',
    'y': 'years',
    }

# DAYS = set(map(str.lower, EnglishLocale.day_abbreviations[1:] + EnglishLocale.day_names[1:]))
# """{'fri', 'friday', ...}"""


TIMEUNIT_REMAINDER = "(?:ec(?:ond)?|in(ute)?|ay|eek|onth|(ou|uarte|ea)?r)?"
# for token_num in range(1, 8):
# TIMEUNITS = "(?:sec(?:ond)?|in(ute)?|ay|eek|onth|(ou|uarte|ea)?r)?s?"

HUMAN_RELATIVE = re.compile(
        rf' *(?P<future>in )? *'
        rf'(?P<quantity_1>(an?|\d+)) *(?P<time_unit_1>(?P<time_unit_1_first_char>([smhdwqy])){TIMEUNIT_REMAINDER})s? *,? *(?:and)? *'
        rf'('
        rf'(?P<quantity_2>(an?|\d+)) *(?P<time_unit_2>(?P<time_unit_2_first_char>([smhdwqy])){TIMEUNIT_REMAINDER})s? *,? *(?:and)? *'
        rf'('
        rf'(?P<quantity_3>(an?|\d+)) *(?P<time_unit_3>(?P<time_unit_3_first_char>([smhdwqy])){TIMEUNIT_REMAINDER})s?'
        rf')?'
        rf')?'
        rf' *'
        rf'(?P<past>ago)? *$',
        re.IGNORECASE
        )
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

def dehumanize_other_if_str(method: Callable[["XArrow", Any], bool]) -> Callable[["XArrow", Any], bool]:
    def wrapper(self: "XArrow", other: Any) -> bool:
        if isinstance(other, str):
            other = self.dehumanize(other)
        return method(self, other)
    return wrapper

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
        self._HHmm = None
        self._HHmmss = None
        self._DDMMYY = None
        self._DDMMYYHHmmss = None
        self._full = None
        self._colored = None
        super().__init__(year, month, day, hour, minute, second, microsecond=0, tzinfo=tzinfo, **kwargs)
    
    @property
    def colored(self):
        if not self._colored:
            self._colored = c.time(str(self))
        return self._colored
    
    @classmethod
    def now(cls, tzinfo: Optional[dt_tzinfo] = None) -> "XArrow":
        rv = super().now(tzinfo)
        return rv
    
    @classmethod
    def from_formatted(cls, date: Union[str, dt_time, "XArrow"]) -> "XArrow":
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
    def from_day(cls, day: Union[str, dt_time, "XArrow"]) -> "XArrow":  # perf: µs
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

    def _dehumanize_relative(self, input_string: Union[str, dt_time, "XArrow"]) -> "XArrow":
        """
        >>> XArrow._dehumanize_relative('3m ago')
        <XArrow ...>
        """
        match = HUMAN_RELATIVE.fullmatch(input_string)
        if not match:
            raise ValueError(f"Don't understand {input_string = !r}")
        match_group_dict = match.groupdict()
    
        # Both "3m" and "3m ago" are past, so only "in 3m" is future
        sign = +1 if match_group_dict.get("future") else -1
    
        quantity_1 = match_group_dict['quantity_1']
        try:
            quantity_1 = int(quantity_1) * sign
        except ValueError:
            # "a day ago"
            quantity_1 = sign
    
        time_unit_1_first_char = match_group_dict['time_unit_1_first_char']
        time_unit_1 = match_group_dict['time_unit_1']
        if time_unit_1_first_char == 'm' and time_unit_1 == 'month':
            time_unit_1_first_char = 'M'
        time_unit_1_plural = TIME_UNITS_FIRST_DIGIT_TO_PLURAL[time_unit_1_first_char]
        shift_kwargs = {time_unit_1_plural: quantity_1}
    
        if quantity_2 := match_group_dict.get('quantity_2'):
            try:
                quantity_2 = int(quantity_2) * sign
            except ValueError:
                quantity_2 = sign
            time_unit_2_first_char = match_group_dict['time_unit_2_first_char']
            time_unit_2 = match_group_dict['time_unit_2']
            if time_unit_2_first_char == 'm' and time_unit_2 == 'month':
                time_unit_2_first_char = 'M'
            time_unit_2_plural = TIME_UNITS_FIRST_DIGIT_TO_PLURAL[time_unit_2_first_char]
            shift_kwargs.update({time_unit_2_plural: quantity_2})
        
            if quantity_3 := match_group_dict.get('quantity_3'):
                try:
                    quantity_3 = int(quantity_3) * sign
                except ValueError:
                    quantity_3 = sign
            
                time_unit_3 = match_group_dict['time_unit_3']
                time_unit_3_first_char = match_group_dict['time_unit_3_first_char']
                if time_unit_3_first_char == 'm' and time_unit_3 == 'month':
                    time_unit_3_first_char = 'M'
                time_unit_3_plural = TIME_UNITS_FIRST_DIGIT_TO_PLURAL[time_unit_3_first_char]
                shift_kwargs.update({time_unit_3_plural: quantity_3})
        parsed = self.shift(**shift_kwargs)
        return parsed

    @classmethod
    def from_absolute(cls, time: Union[str, dt_time, "XArrow"]) -> "XArrow":
        """
        >>> XArrow.from_absolute('09:45')
        <XArrow ...>
        """
        # if `time` specifies second, it would get updated
        # otherwise expected behavior is like constructing datetime.time(23, 59) (second==0)
        now = cls.now().replace(second=0)
        
        updated = now.update(time)
        return updated
    
    # noinspection PyMethodOverriding,PyMethodParameters
    @overload
    def dehumanize(input_string: str, locale: str = "local") -> "XArrow": ...
    @overload
    def dehumanize(self: "XArrow", input_string: str, locale: str = "local") -> "XArrow": ...
    # noinspection PyMethodParameters
    def dehumanize(self_or_input_string, input_string_or_locale: str = None, locale: str = "local") -> "XArrow":
        if isinstance(self_or_input_string, str):
            called_static = True
            input_string = self_or_input_string
        else:
            called_static = False
            input_string = input_string_or_locale

        input_string_lowercase = input_string.lower()
        if input_string_lowercase in ('now', 'today', 'just now', 'right now'):
            return XArrow.now()
        
        if input_string_lowercase == 'yesterday':
            return XArrow.now().shift(days=-1)
        
        if input_string_lowercase == 'tomorrow':
            return XArrow.now().shift(days=1)
        
        if called_static:
            self: XArrow = XArrow.now()
        else:
            self: XArrow = self_or_input_string
        rv = self._dehumanize_relative(input_string)
        return rv
    
    @classmethod
    def from_human(cls, human_time: Union[str, dt_time, "XArrow"] = "now") -> "XArrow":
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
        
        # '3m' / 'now', 'today', 'yesterday', 'tomorrow'
        with suppress(ValueError):
            return cls.dehumanize(human_time)
        
        # 'thurs', ...
        with suppress(ValueError):
            return cls.from_day(human_time)
        
        
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
    
    def update(self, time: Union[str, dt_time, "XArrow"]) -> "XArrow":
        """
        >>> self.update('09:45')
        <XArrow ...>
        """
        if isinstance(time, XArrow):
            return time
        
        replace = {}
        if isinstance(time, str):
            if FORMATS.date_separator in time and FORMATS.time_separator in time:
                raise NotImplementedError(f"Looks like {time = !r} is a datetime. Currently can only update time or date.")
            time_match = FORMATS.time_format_re.match(time)
            if time_match:
                
                match_dict = time_match.groupdict()
            else:
                date_match = FORMATS.date_format_re.match(time)
                if not date_match:
                    raise ValueError(f"{time = !r} doesn't match time format {FORMATS.time_format_re}, nor date format {FORMATS.date_format_re}")
                match_dict = date_match.groupdict()
            if (year := match_dict.get('year')) is not None:
                replace['year'] = int(year)
            if (month := match_dict.get('month')) is not None:
                replace['month'] = int(month)
            if (day := match_dict.get('day')) is not None:
                replace['day'] = int(day)
            if (hour := match_dict.get('hour')) is not None:
                replace['hour'] = int(hour)
            if (minute := match_dict.get('minute')) is not None:
                replace['minute'] = int(minute)
            if (second := match_dict.get('second')) is not None:
                replace['second'] = int(second)
        
        else: # time or datetime
            for name in self._ATTRS:
                if name != 'microsecond' and (attr := getattr(time, name, None)):
                    replace[name] = attr
        
        rv = self.replace(**replace)
        return rv
    
    @overload
    def isoweekday(self, human: NoneType = None) -> int:
        """1"""
    @overload
    def isoweekday(self, human: Literal['short'] = 'short') -> str:
        """'Wed'"""
    @overload
    def isoweekday(self, human: Literal['full'] = 'full') -> str:
        """'Wednesday'"""
    def isoweekday(self, human=None):
        if not human:
            return isoweekday(self.strftime('%a'))
        if human == 'short':
            return self.strftime('%a')
        if human == 'full':
            return self.strftime('%A')
        raise ValueError(f"Bad 'human' value, can be either None, 'short' or 'full'. Got XArrow.isoweekday({human = !r})")

    @property
    def HHmm(self):
        if not self._HHmm:
            self._HHmm: str = self.format(FORMATS.short_time)
        return self._HHmm
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
            self._DDMMYYHHmmss: str = self.format(f'{FORMATS.datetime}')
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

    __eq__ = dehumanize_other_if_str(Arrow.__eq__)
    __ne__ = dehumanize_other_if_str(Arrow.__ne__)
    __gt__ = dehumanize_other_if_str(Arrow.__gt__)
    __ge__ = dehumanize_other_if_str(Arrow.__ge__)
    __lt__ = dehumanize_other_if_str(Arrow.__lt__)
    __le__ = dehumanize_other_if_str(Arrow.__le__)

class XArrowFactory(ArrowFactory):
    type: Type[XArrow]
    
    def __init__(self, type: Type[XArrow] = XArrow) -> None:
        super().__init__(type)
    
    get: Callable[..., XArrow]


# Docs say factory = arrow.ArrowFactory(XArrow)
# https://arrow.readthedocs.io/en/latest/#factories
xarrow_factory = XArrowFactory()