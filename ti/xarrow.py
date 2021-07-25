from ti import times
from typing import Type, Optional, Any

from arrow import Arrow, ArrowFactory
from arrow.arrow import TZ_EXPR

import ti.color as c


class XArrow(Arrow):

    def __init__(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0, tzinfo: Optional[TZ_EXPR] = None, **kwargs: Any) -> None:
        super().__init__(year, month, day, hour, minute, second, microsecond, tzinfo, **kwargs)
        self.colored = c.time(self)
        self._HHmmss = None
        self._DDMMYY = None
        self._DDMMYYHHmmss = None
        self._full = None

    @property
    def HHmmss(self):
        if not self._HHmmss:
            self._HHmmss: str = times.reformat(self, times.FORMATS.time)
        return self._HHmmss

    @property
    def DDMMYY(self):
        if not self._DDMMYY:
            self._DDMMYY: str = times.reformat(self, times.FORMATS.date)
        return self._DDMMYY

    @property
    def DDMMYYHHmmss(self):
        if not self._DDMMYYHHmmss:
            self._DDMMYYHHmmss: str = times.reformat(self, times.FORMATS.date_time)
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
