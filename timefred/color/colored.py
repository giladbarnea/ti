from typing import Callable
from timefred import color as c

from timefred.field import Field
from timefred.space import StringSpace


class Colored(StringSpace):
    brush: Callable = Field(optional=True)
    
    # def __init__(self, seq: object='', brush: Callable = None) -> None:
    #     UserString.__init__(self, seq)
    
    @property
    def colored(self):
        return self.brush(self)

class TaskString(Colored):
    brush = c.task
