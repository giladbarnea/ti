from typing import Optional

from multimethod import multimethod
from pydantic import BaseModel, Field

from timefred import color as c
from timefred.note import Note
from timefred.time import XArrow, Timespan
from timefred.util import normalize_str


class Item(BaseModel):
    name: str
    _name_colored: str = ''
    start = Field(default_factory=XArrow.from_formatted)
    end = Field(default_factory=XArrow.from_formatted,
                #optional=True
                )
    notes = Field(list[Note])
    tags: Optional[set[str]]
    jira: Optional[str]
    timespan: Timespan

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    # def __init__(self, name, start, end=None, notes=None, tags=None, jira=None) -> None:
    # 	super().__init__(dict(name=name,
    # 						  start=start,
    # 						  end=end,
    # 						  notes=notes or [],
    # 						  tags=tags or set(),
    # 						  jira=jira))

    # @property
    # def notes(self) -> list[Note]:
    # 	if self.__cache__.notes:
    # 		return self._notes
    # 	for i, note in enumerate(self._notes):
    # 		if not isinstance(note, Note):
    # 			self._notes[i] = Note(note)
    # 	self.__cache__.notes = True
    # 	return self._notes

    @property
    def name_colored(self):
        if not self._name_colored:
            self._name_colored = c.task(self.name)
        return self._name_colored

    # @property
    # def start(self) -> XArrow:
    # 	if self._start and not isinstance(self._start, Arrow):
    # 		self._start = XArrow.from_formatted(self._start)
    # 	return self._start

    # @start.setter
    # def start(self, val):
    # 	self._start = val

    # @property
    # def end(self) -> XArrow:
    # 	if self._end and not isinstance(self._end, Arrow):
    # 		self._end = XArrow.from_formatted(self._end)
    # 	return self._end
    #
    # @end.setter
    # def end(self, val):
    # 	self._end = val

    # @property
    # def timespan(self) -> Timespan:
    # 	if not self._timespan:
    # 		self._timespan = Timespan(self.start, self.end)
    # 	return self._timespan

    @multimethod
    def has_similar_name(self, other: 'Item') -> bool:
        return self.has_similar_name(other.name)

    @multimethod
    def has_similar_name(self, other: str) -> bool:
        return normalize_str(self.name) == normalize_str(other)
