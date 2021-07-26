import re
from collections import defaultdict, UserDict, namedtuple
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Tuple, Literal, TypeVar, MutableMapping, Set

from timefred import color as c
from timefred.item import Item
from timefred.note import Note
from timefred.store import store
from timefred.times import human2arrow, secs2human, now, arrows2rel_time
from timefred.xarrow import XArrow

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
    name: str = ''
    is_current: bool = False
    timespans: List[Timespan] = field(default_factory=list)  # Multiple (start, end) pairs
    notes: List[Note] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)

    def seconds(self) -> int:
        return sum(self.timespans)

    def human_duration(self) -> str:
        return secs2human(self.seconds())

    def earliest_start(self) -> XArrow:
        return min(timespan.start for timespan in self.timespans)

    def pretty(self, detailed: bool = True, width: int = 24):
        if detailed:
            time = "\n  \x1b[2m"
            if self.notes:
                time += '\n  ' + c.grey150('Times')

            for start, end in self.timespans:
                if end:
                    time += f'\n  {start.HHmmss} → {end.HHmmss} ({end - start})'
                else:
                    time += f'\n  {start.HHmmss}'

            if self.notes:
                time += '\n\n  ' + c.grey150('Notes')

            # for note_time, note_content in sorted(log_entry.notes, key=lambda _n: _n[0] if _n[0] else '0'):
            for note_content, note_time in filter(bool, self.notes):
                if note_time:
                    time += f'\n  {note_content} ({note_time.HHmmss})'
                else:
                    time += f'\n  {note_content}'

            time += "\x1b[0m\n"
        else:
            earliest_start_time = self.earliest_start()
            time = c.i(c.dim('   started ' + earliest_start_time.HHmmss))

        if self.is_current:
            name = c.title(self.name)
        else:
            name = c.w200(self.name)

        if detailed:
            name += f'  {", ".join(c.dim(c.tag2(_tag)) for _tag in self.tags)}'

        pretty = ' '.join([c.ljust_with_color(name, width),
                           '\x1b[2m\t\x1b[0m ',
                           self.human_duration(),
                           time])
        return pretty


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

    def human_duration(self):
        return secs2human(self.total_seconds())

from pdbpp import break_on_exc
@break_on_exc
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
                # We have iterated past period
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
        log_entry.name = item.name
        log_entry.notes.extend(item.notes)
        log_entry.tags |= item.tags

        timespan = Timespan(item.start, item.end or _now)
        log_entry.timespans.append(timespan)

        if not timespan.end:
            log_entry.is_current = True


    title = c.title(period_arrow.full)
    ago = arrows2rel_time(_now, period_arrow)
    if ago:
        title += f' {c.dim("| " + ago)}'

    print(title + '\n')
    if not _log:
        return
    name_column_width = max(*map(len, map(lambda entry: entry.name, _log.values())), 24)
    if groupby:
        for _tag, names in by_tag.items():
            print(c.tag(_tag))
            for name in names:
                print_log(name, _log[name], current, detailed, name_column_width)
        return

    for name, log_entry in _log.sorted_entries():
        print(log_entry.pretty(detailed, name_column_width))

    print(c.title('Total: ') + re.sub(r'\d', lambda match: f'{c.digit(match.group())}', _log.human_duration()))
