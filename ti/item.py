from typing import List, Optional, Callable, Any

from arrow import Arrow

from ti import color as c
from ti.dikt import Dikt
from ti.times import formatted2arrow


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


# @dataclass
class Item(Dikt):
	name: str
	name_colored: str
	start: Arrow
	end: Optional[Arrow]
	notes: Optional[List[str]]
	tags: Optional[List[str]]
	jira: Optional[str]

	def __init__(self, name, start, end=None, notes=None, tags=None, jira=None) -> None:
		super().__init__(dict(_name=name,
							  _start=start,
							  _end=end,
							  notes=notes if notes is not None else [],
							  tags=tags if tags is not None else [],
							  # name_colored=c.b(c.rgb(name, 58, 150, 221)),
							  name_colored=c.task(name),
							  jira=jira
							  ))

	@property
	def name(self):
		return self._name

	@property
	def start(self) -> Arrow:
		if self._start and not isinstance(self._start, Arrow):
			self._start = formatted2arrow(self._start)
		return self._start
	@start.setter
	def start(self, val):
		self._start = val


	@property
	def end(self) -> Arrow:
		if self._end and not isinstance(self._end, Arrow):
			self._end = formatted2arrow(self._end)
		return self._end

	@end.setter
	def end(self, val):
		self._end = val
