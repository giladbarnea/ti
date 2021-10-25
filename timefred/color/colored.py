from typing import Callable


class Colored:
    def __init__(self, val='', brush: Callable = None):
        self._raw = val
        self._brush = brush
        self.colored = brush(val)
    
    def __set__(self, instance, value):
        self._raw = value
        self.colored = self._brush(value)
    
    def __str__(self):
        return self._raw
