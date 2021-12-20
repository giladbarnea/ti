# from dataclasses import dataclass, field
from datetime import timedelta
from collections.abc import Iterator
from typing import Optional

from multimethod import multimethod

# from pydantic import Field, BaseModel
from timefred.space import Field, AttrDictSpace, Space, DictSpace
from timefred.time.timeutils import secs2human
from timefred.time.xarrow import XArrow


# @dataclass
class Timespan(DictSpace):
    # todo: XArrow - XArrow -> Timespan?
    #       inherit from timedelta?
    #       XArrow.span() -> (XArrow, XArrow)?
    # start = Field(cast=XArrow)
    start: XArrow = Field(cast=XArrow.from_absolute)
    # end:   Optional[XArrow] = None
    # end = Field(optional=True, cast=XArrow)
    end: XArrow = Field(optional=True, cast=XArrow.from_absolute)

    def __repr__(self):
        short_id = f'{str(id(self))[-4:]}'
        start = self.start
        end = self.end
        representation = f'{self.__class__.__qualname__} ({start=!r}, {end=!r}) <{short_id}>'
        return representation

    @multimethod
    def __radd__(self, other) -> int:
        other_timedelta = other.timedelta()
        other_total_seconds = other_timedelta.total_seconds()
        other_total_seconds_int = int(other_total_seconds)
        return self.__radd__(other_total_seconds_int)
    
    @multimethod
    def __radd__(self, other: int) -> int:
        self_seconds = self.seconds()
        return self_seconds + other
        # try:
        #     return self_seconds + int(other.timedelta().total_seconds())
        # except AttributeError: # other is int
        #     return self_seconds + other
    def __lt__(self, other):
        return self.start > other.start
    
    def __add__(self, other) -> int:
        self_seconds = self.seconds()
        other_seconds = other.seconds()
        return self_seconds + other_seconds
    
    def __bool__(self):
        return bool(self.start) or bool(self.end)

    def __iter__(self) -> Iterator[Optional[XArrow]]:
        yield self.start
        yield self.end
        # return super().__iter__()

    def timedelta(self) -> timedelta:
        if self.end:
            return self.end - self.start
        else:
            return timedelta(seconds=0)
    #
    def seconds(self) -> int:
        td = self.timedelta()
        td_total_seconds = td.total_seconds()
        return int(td_total_seconds)
    
    def human_duration(self) -> str:
        return secs2human(self.seconds())
