import re
from collections import defaultdict, UserDict, namedtuple
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Tuple, Literal, TypeVar, MutableMapping, Optional, overload, Any

from ti import color as c
from ti.item import Item
from ti.note import Note
from ti.store import store
from ti.times import human2arrow, secs2human, now, arrows2rel_time
from ti.xarrow import XArrow

# from loguru import logger

NOTE_TIME_RE = re.compile(r'(.+) \(([\d/: ]+)\)', re.IGNORECASE)


class Timespan(namedtuple('Timespan', 'start end')):
	start: XArrow
	end: XArrow

	def __radd__(self, other):
		self_td = self.timedelta()
		try:
			return self_td + other.timedelta()
		except AttributeError:
			return self_td.total_seconds() + other

	def timedelta(self) -> timedelta:
		return self.end - self.start

	def seconds(self) -> int:
		return int(self.timedelta().total_seconds())

	def human_duration(self) -> str:
		return secs2human(self.seconds())


@dataclass
class LogEntry:
	timespans: List[Timespan] = field(default_factory=list)  # Multiple (start, end) pairs
	notes: List[Note] = field(default_factory=list)
	tags: List[str] = field(default_factory=list)

	def seconds(self) -> int:
		return sum(self.timespans)

	def human_duration(self) -> str:
		return secs2human(self.seconds())

	def earliest_start(self) -> XArrow:
		return min(timespan.start for timespan in self.timespans)


K = TypeVar('K')


class Log(UserDict, MutableMapping[K, LogEntry]):
	def __getitem__(self, key):
		if key in self.data:
			return super().__getitem__(key)
		self.data[key] = LogEntry()
		return self.data[key]

	def sorted_entries(self) -> List[Tuple[K, LogEntry]]:
		"""Takes each log entry's earliest start time and compares to other log entries"""

		def by_earliest_start(name_log_entry_pair):
			log_entry = name_log_entry_pair[1]
			return log_entry.earliest_start()

		return sorted(self.items(), key=by_earliest_start)

	def total_seconds(self) -> int:
		total = 0
		for name, log_entry in self.items():
			duration = int(log_entry.seconds())
			total += duration
		return total

def log(period="today", *, detailed=True, groupby: Literal['t', 'tag'] = None):
	if groupby and groupby not in ('t', 'tag'):
		raise ValueError(f"log({period = }, {groupby = }) groupby must be either 't' | 'tag'")
	data = store.load()
	work = data['work'] + data['interrupt_stack']
	_log = Log()
	current = None
	period_arrow = human2arrow(period)
	_now = now()

	by_tag = defaultdict(set)

	for i, item in enumerate(map(lambda w: Item(**w), reversed(work))):
		if item.start.DDMMYY != period_arrow.DDMMYY:
			if period_arrow > item.start:
				# In the past
				break
			continue
		if period_arrow.month != item.start.month and period_arrow.year != item.start.year:
			break
			# noinspection PyUnreachableCode
			if groupby and groupby in ('t', 'tag'):
				if not tags:
					by_tag[None].add(name)
				else:
					for t in tags:
						by_tag[t].add(name)

		log_entry = _log[item.name]
		log_entry.notes.extend(item.notes)
		log_entry.tags = item.tags

		timespan = Timespan(item.start, item.end or _now)
		log_entry.timespans.append(timespan)


		if not timespan.end:
			current = item.name

	# Calculate total duration
	name_col_len = 0
	for name, log_entry in _log.items():
		name_col_len = max(name_col_len, len(name), 24)

	total_secs = _log.total_seconds()
	title = c.title(period_arrow.full)
	ago = arrows2rel_time(_now, period_arrow)
	if ago:
		title += f' {c.dim("| " + arrows2rel_time(_now, period_arrow))}'
	# if len(period) > 2:
	#     title = period.title()
	# else:
	#     title = f"{period[0]} {timespans.ABBREVS[period[1]]} ago"
	print(title + '\n' if detailed else '')

	if groupby:
		for _tag, names in by_tag.items():
			print(c.tag(_tag))
			for name in names:
				print_log(name, _log[name], current, detailed, name_col_len)
		return

	for name, log_entry in _log.sorted_entries():
		print_log(name, log_entry, current, detailed, name_col_len)

	print(c.title('Total: ') + re.sub(r'\d', lambda match: f'{c.digit(match.group())}', secs2human(total_secs)))



def print_log(name: str, log_entry: LogEntry, current: str, detailed: bool, name_col_len: int):
	if detailed:
		time = "\n  \x1b[2m"
		if log_entry.notes:
			time += '\n  ' + c.grey150('Times')

		for start, end in log_entry.timespans:
			if end:
				time += f'\n  {start.HHmmss} → {end.HHmmss} ({end - start})'
			else:
				time += f'\n  {start.HHmmss}'

		if log_entry.notes:
			time += '\n\n  ' + c.grey150('Notes')

		# for note_time, note_content in sorted(log_entry.notes, key=lambda _n: _n[0] if _n[0] else '0'):
		for note_content, note_time in filter(bool, log_entry.notes):
			if note_time:
				time += f'\n  {note_content} ({note_time.HHmmss})'
			else:
				time += f'\n  {note_content}'

		time += "\x1b[0m\n"
	else:
		earliest_start_time = log_entry.earliest_start()
		time = c.i(c.dim('   started ' + earliest_start_time.HHmmss))

	if current == name:
		name = c.title(name)
	else:
		name = c.w200(name)

	if detailed:
		name += f'  {", ".join(c.dim(c.tag2(_tag)) for _tag in log_entry.tags)}'

	print(c.ljust_with_color(name, name_col_len),
		  '\x1b[2m\t\x1b[0m ',
		  log_entry.human_duration(),
		  time)
