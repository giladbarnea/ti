from typing import Optional

from multimethod import multimethod
from pydantic import BaseModel, Field, validator, root_validator

from timefred import color as c
from timefred.note import Note
from timefred.time import XArrow, Timespan
from timefred.util import normalize_str
# from pdbr import set_trace

# set_trace()

class Item(BaseModel):
    # class Config:
    #     arbitrary_types_allowed=True
    # name: str
    _name_colored: str = ''
    # start: XArrow = Field(default_factory=XArrow.from_formatted)
    # end: Optional[XArrow] = Field(default_factory=XArrow.from_formatted)
    # notes: list[Note] = Field(default_factory=list[Note])
    # tags: Optional[set[str]] = Field(default_factory=set[str])
    # jira: Optional[str] = Field(default_factory=str)
    # timespan: Optional[Timespan] = Field(default_factory=Timespan)
    
    
    # def __init__(self, **kwargs) -> None:
    #     super().__init__(**kwargs)
    
    # @root_validator(pre=True)
    # def root_validator(self, values):
    #     print()
   
    # @validator('start', check_fields=False)
    # def xarrow_validator(cls, v):
    #     print('\n\nxarrow_validator\n\n')
    #     return v
   
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

    # @property
    # def name_colored(self):
    #     if not self._name_colored:
    #         self._name_colored = c.task(self.name)
    #     return self._name_colored

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

    # @multimethod
    # def has_similar_name(self, other: 'Item') -> bool:
    #     return self.has_similar_name(other.name)
    #
    # @multimethod
    def has_similar_name(self, other: str) -> bool:
        return normalize_str(self.name) == normalize_str(other)
