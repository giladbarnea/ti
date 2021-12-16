from dataclasses import dataclass, field
from datetime import timedelta

from multimethod import multimethod

# from pydantic import Field, BaseModel
from timefred.space import Field, AttrDictSpace, Space, DictSpace
from timefred.time.timeutils import secs2human
from timefred.time.xarrow import XArrow


# @dataclass
class Timespan(DictSpace):
# class Timespan:
    # todo: XArrow - XArrow -> Timespan?
    #       inherit from timedelta?
    #       XArrow.span() -> (XArrow, XArrow)?
    # class Config:
    #     arbitrary_types_allowed = True
    # start = Field(cast=XArrow)
    start: XArrow = Field(cast=XArrow.from_absolute)
    # end:   Optional[XArrow] = None
    # end = Field(optional=True, cast=XArrow)
    end: XArrow = Field(optional=True, cast=XArrow.from_absolute)
    
    @multimethod
    def __radd__(self, other) -> int:
        return self.__radd__(int(other.timedelta().total_seconds()))
    
    @multimethod
    def __radd__(self, other: int) -> int:
        self_seconds = self.seconds()
        return self_seconds + other
        # try:
        #     return self_seconds + int(other.timedelta().total_seconds())
        # except AttributeError: # other is int
        #     return self_seconds + other
    
    def __add__(self, other) -> int:
        self_seconds = self.seconds()
        other_seconds = other.seconds()
        return self_seconds + other_seconds
    
    def __bool__(self):
        return bool(self.start) or bool(self.end)
    
    def timedelta(self) -> timedelta:
        return self.end - self.start
    
    def seconds(self) -> int:
        return int(self.timedelta().total_seconds())
    
    def human_duration(self) -> str:
        return secs2human(self.seconds())
