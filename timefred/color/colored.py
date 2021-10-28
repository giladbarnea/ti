from typing import Callable

from timefred.field import Field
from timefred.has_fields import HasFieldsString


class Colored(HasFieldsString):
    brush: Callable = Field(optional=True)
    
    # def __init__(self, seq: object='', brush: Callable = None) -> None:
    #     UserString.__init__(self, seq)
    
    @property
    def colored(self):
        return self.brush(self)
