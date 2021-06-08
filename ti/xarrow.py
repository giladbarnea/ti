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
        self._MMDDYY = None
        self._MMDDYYHHmmss = None
        self._full = None

    @property
    def HHmmss(self):
        if not self._HHmmss:
            self._HHmmss: str = times.reformat(self, "HH:mm:ss")
        return self._HHmmss

    @property
    def MMDDYY(self):
        if not self._MMDDYY:
            self._MMDDYY: str = times.reformat(self, times.FMT)
        return self._MMDDYY

    @property
    def MMDDYYHHmmss(self):
        if not self._MMDDYYHHmmss:
            self._MMDDYYHHmmss: str = times.reformat(self, times.DT_FMT)
        return self._MMDDYYHHmmss

    @property
    def full(self):
        """'Thursday 05/20/21'"""
        if not self._full:
            self._full: str = self.strftime('%A %x')
        return self._full


class XArrowFactory(ArrowFactory):
    type: Type[XArrow]

    def __init__(self, type: Type[XArrow] = XArrow) -> None:
        super().__init__(type)


xarrow_factory = XArrowFactory()
