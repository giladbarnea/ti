from typing import Optional, Callable, Any

from arrow import Arrow

from timefred import color as c
from timefred.dikt import Dikt, Field
from timefred.note import Note
from timefred.time import XArrow, Timespan
from multimethod import multimethod

from timefred.util import normalize_str


class myproperty(property):

	def __init__(self, fget: Optional[Callable[[Any], Any]] = ..., fset: Optional[Callable[[Any, Any], None]] = ..., fdel: Optional[Callable[[Any], None]] = ..., doc: Optional[str] = ...) -> None:
		super().__init__(fget, fset, fdel, doc)

	def fget(self) -> Any:
		rv = super().fget()
		# breakpoint()
		return rv

	def getter(self, fget: Callable[[Any], Any]) -> property:
		rv = super().getter(fget)
		# breakpoint()
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
	#name_colored: str = ''
	# start = Field(XArrow.from_formatted)
	start: Field(XArrow.from_formatted)
	end: Optional[Field(XArrow.from_formatted)]
	notes: list[Note]
	tags: Optional[set[str]]
	jira: Optional[str]
	timespan: Timespan

	def __init__(self, name, start, end=None, notes=None, tags=None, jira=None) -> None:
		# super().__init__(dict(name=name,
		# 					  _start=start,
		# 					  _end=end,
		# 					  _name_colored='',
		# 					  _notes=notes if notes is not None else [],
		# 					  tags=tags if tags is not None else {},
		# 					  jira=jira))
		super().__init__(dict(name=name,
							  start=start,
							  end=end,
							  notes=notes or [],
							  tags=tags or set(),
							  jira=jira))

	@property
	def notes(self) -> list[Note]:
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

	# @property
	# def start(self) -> XArrow:
	# 	if self._start and not isinstance(self._start, Arrow):
	# 		self._start = XArrow.from_formatted(self._start)
	# 	return self._start

	# @start.setter
	# def start(self, val):
	# 	self._start = val

	@property
	def end(self) -> XArrow:
		if self._end and not isinstance(self._end, Arrow):
			self._end = XArrow.from_formatted(self._end)
		return self._end

	@end.setter
	def end(self, val):
		self._end = val

	@property
	def timespan(self) -> Timespan:
		if not self._timespan:
			self._timespan = Timespan(self.start, self.end)
		return self._timespan

	@multimethod
	def has_similar_name(self, other: 'Item') -> bool:
		return self.has_similar_name(other.name)

	@multimethod
	def has_similar_name(self, other: str) -> bool:
		return normalize_str(self.name) == normalize_str(other)