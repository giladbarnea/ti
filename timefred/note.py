import re
from collections.abc import Mapping
from multimethod import multimethod

from timefred import color as c
from timefred.space import DictSpace, Field
from timefred.time.xarrow import XArrow
from timefred.util import normalize_str

NOTE_TIME_RE = re.compile(r'(.+) \(([\d/: ]+)\)', re.IGNORECASE)


class Note(DictSpace):
	time: XArrow = Field(default_factory=XArrow.from_absolute, cast=XArrow.from_absolute)
	content: str = Field(default_factory=str)
	
	def __init__(self, note: Mapping) -> None:
		time = next(iter(note))
		content = note[time]
		super().__init__(time=time, content=content)
	
	def __repr__(self):
		return f'{self.__class__.__qualname__}(content = {self.content!r}, time = {self.time!r})'
	# @multimethod
	# def __init__(self, content: str, time: Union[str, XArrow]=None):
	# 	self.content = content
	# 	if not time:
	# 		time = XArrow.now()
	# 	self._time = time
	#
	# @multimethod
	# def __init__(self, note: str):
	# 	match = NOTE_TIME_RE.fullmatch(note)
	# 	if match:
	# 		match_groups = match.groups()
	# 		self.content = match_groups[0]
	# 		self._time = match_groups[1]
	# 	else:
	# 		self.content = note
	# 		self._time = None

	def __iter__(self):
		yield self.content
		yield self.time

	def __bool__(self):
		return bool(self.content)

	def pretty(self, color=True):
		content = c.b(self.content) if color else self.content
		if self.time:
			string = f'{self.time.HHmm}: {content}'
			return c.note(string) if color else string
		return c.note(content) if color else content

	@multimethod
	def is_similar(self, other: "Note") -> bool:
		return self.is_similar(other.content)

	@multimethod
	def is_similar(self, other: str) -> bool:
		other_normalized = normalize_str(other)
		self_normalized = normalize_str(self.content)

		return self_normalized in other_normalized or other_normalized in self_normalized
