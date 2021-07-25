from typing import List, Optional, Callable, Any

from arrow import Arrow

from ti import color as c
from ti.dikt import Dikt
from ti.note import Note
from ti.times import formatted2arrow
from ti.xarrow import XArrow


class myproperty(property):

    def __init__(self, fget: Optional[Callable[[Any], Any]] = ..., fset: Optional[Callable[[Any, Any], None]] = ..., fdel: Optional[Callable[[Any], None]] = ..., doc: Optional[str] = ...) -> None:
        super().__init__(fget, fset, fdel, doc)

    def fget(self) -> Any:
        rv = super().fget()
        breakpoint()
        return rv

    def getter(self, fget: Callable[[Any], Any]) -> property:
        rv = super().getter(fget)
        breakpoint()
        return rv

    def __get__(self, obj: Any, type: Optional[type] = ...) -> Any:
        rv = super().__get__(obj, type)
        return rv

    def __getattr__(self, name: str) -> Any:
        print(f'{name = }')
        if name == 'pretty':
            breakpoint()
        return super().__getattr__(name)


# def __get__(self, obj: Any, type: Optional[type] = ...) -> Any:
# 	rv = super().__get__(obj, type)
# 	return rv


class Item(Dikt):
    name: str
    name_colored: str
    _start: XArrow
    _end: Optional[XArrow]
    notes: List[Note]
    tags: Optional[List[str]]
    jira: Optional[str]

    def __init__(self, name, start, end=None, notes=None, tags=None, jira=None) -> None:
        super().__init__(dict(name=name,
                              _start=start,
                              _end=end,
                              _name_colored='',
                              _notes=notes if notes is not None else [],
                              tags=tags if tags is not None else [],
                              jira=jira))

    @property
    def notes(self):
        if self.__cache__.notes:
            return self._notes
        for i, note in enumerate(self._notes):
            if not isinstance(note, Note):
                self._notes[i] = Note(note)
        self.__cache__.notes = True
        return self._notes
    @property
    def name_colored(self):
        if not self._name_colored:
            self._name_colored = c.task(self.name)
        return self._name_colored

    @property
    def start(self) -> XArrow:
        if self._start and not isinstance(self._start, Arrow):
            self._start = formatted2arrow(self._start)
        return self._start

    @start.setter
    def start(self, val):
        self._start = val

    @property
    def end(self) -> XArrow:
        if self._end and not isinstance(self._end, Arrow):
            self._end = formatted2arrow(self._end)
        return self._end

    @end.setter
    def end(self, val):
        self._end = val
