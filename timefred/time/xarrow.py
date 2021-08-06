from datetime import datetime
from typing import Type, Optional, Any, Union

from arrow import Arrow, ArrowFactory
from arrow.arrow import TZ_EXPR

import timefred.color as c
from timefred.util import confirm
from timefred.config import config
FORMATS = config.time.formats
TZINFO = config.time.tz


class XArrow(Arrow):
    def __init__(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0, tzinfo: Optional[TZ_EXPR] = None, **kwargs: Any) -> None:
        super().__init__(year, month, day, hour, minute, second, microsecond, tzinfo, **kwargs)
        self.colored = c.time(self)
        self._HHmmss = None
        self._DDMMYY = None
        self._DDMMYYHHmmss = None
        self._full = None

    @classmethod
    def from_formatted(cls, date: Union[str, 'XArrow']) -> 'XArrow':
        if isinstance(date, Arrow):
            if not isinstance(date, XArrow) \
                    and confirm(f'XArrow.from_formatted(date) is regular Arrow, debug?'):
                breakpoint()
            return date
        if ' ' in date:
            # "19/04/21 10:13:11" → arrow(...)
            return xarrow_factory.get(date, FORMATS.date_time, tzinfo=TZINFO)
        if '/' in date:
            # "19/04/21" → arrow(...)
            if date.count('/') == 1:
                date += '/' + str(datetime.today().year)[-2:]
            return xarrow_factory.get(date, FORMATS.date, tzinfo=TZINFO)

        # "10:13:11" → datetime(...)
        today = datetime.today()
        return XArrow(today.year, today.month, today.day, *map(int, date.split(':')))

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
            self._DDMMYYHHmmss: str = self.format(FORMATS.date_time)
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
