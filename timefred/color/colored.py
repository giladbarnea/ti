from collections import UserString
from typing import Callable

from timefred.field import Field, field
from timefred.has_fields import HasFieldsString, HasFields


class Colored(HasFieldsString):
    brush: Callable = Field(optional=True)
    # raw: str = Field(default='', optional=True)
    def __init__(self, seq: object='', brush: Callable = None) -> None:
        UserString.__init__(self, seq)
        # self._brush = brush
        # self.colored = brush(self)
    
    # @field(optional=True)
    @property
    def colored(self):
        return self.brush(self.data)
    
    # def __set__(self, instance, value):
    #     self._raw = value
    #     self.colored = self._brush(value)
    #
    # def __str__(self):
    #     return self._raw
