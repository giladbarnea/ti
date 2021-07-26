import re
from typing import Optional, Union

from arrow import Arrow

from timefred import color as c
from timefred.times import formatted2arrow
from timefred.xarrow import XArrow

NOTE_TIME_RE = re.compile(r'(.+) \(([\d/: ]+)\)', re.IGNORECASE)


class Note:
	time: Optional[XArrow]
	content: str

	def __init__(self, note: str):
		match = NOTE_TIME_RE.fullmatch(note)
		if match:
			match_groups = match.groups()
			self.content = match_groups[0]
			self._time = match_groups[1]
		else:
			self.content = note
			self._time = None

	def __iter__(self):
		yield self.content
		yield self.time

	def __bool__(self):
		return bool(self.content)

	def __str__(self) -> str:
		return f'{self.content} ({self.time.HHmmss})' if self.time else self.content

	def pretty(self):
		return c.note(f'{c.b(self.content)} ({self.time.HHmmss})') if self.time else c.b(self.content)

	@property
	def time(self) -> XArrow:
		if self._time and not isinstance(self._time, Arrow):
			self._time = formatted2arrow(self._time)
		return self._time

	def looks_same(self, other: Union[str, 'Note']) -> bool:
		def _normalize(_s: str) -> str:
			return re.sub(r'\W', '', _s.lower())

		try:
			other_normalized = _normalize(other)
		except AttributeError:
			other_normalized = _normalize(other.content)
		self_normalized = _normalize(self.content)

		return self_normalized in other_normalized or other_normalized in self_normalized
