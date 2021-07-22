import re
from collections import defaultdict, UserDict, namedtuple
from dataclasses import dataclass
from datetime import timedelta, datetime
from itertools import dropwhile
from typing import List, Tuple, Literal, Optional, Mapping

# from loguru import logger
from rich import print as rprint

from ti import color as c
from ti.item import Item
from ti.note import Note
from ti.store import store
from ti.times import human2arrow, secs2human, now, arrows2rel_time
from ti.xarrow import XArrow

note_time_re = re.compile(r'(.+) \(([\d/: ]+)\)', re.IGNORECASE)

class Timespan(namedtuple('Timespan','start end')):
    start: XArrow
    end: XArrow

class LogEntry:
    times: List[Timespan] = []  # Multiple (start, end) pairs
    notes: List[Note] = []
    duration: timedelta = timedelta()
    tags: List[str] = []
    pretty: str

class Log(UserDict):
    def __getitem__(self, key):
        if key in self.data:
            return super().__getitem__(key)
        self.data[key] = LogEntry()
        return self.data[key]


def log(period="today", *, detailed=True, groupby: Literal['t', 'tag'] = None):
    if groupby and groupby not in ('t', 'tag'):
        raise ValueError(f"log({period = }, {groupby = }) groupby must be either 't' | 'tag'")
    data = store.load()
    work = data['work'] + data['interrupt_stack']
    # _log = defaultdict(lambda: {'duration': timedelta(), 'times': [], 'notes': []})
    # _log = defaultdict(LogEntry)
    _log = Log()
    current = None
    period_arrow = human2arrow(period)
    _now = now()

    by_tag = defaultdict(set)
    # try:
    # 	item = next(item for item in map(lambda w: Item(**w), reversed(work)) if item.start.full == period_arrow.full)
    # except StopIteration:
    # 	# Optimization: for loop, stop when already passed
    # 	print(f"{c.orange('Missing')} logs for {period_arrow.full}")
    # 	return False
    stop = False
    total_secs = 0
    for i, item in enumerate(map(lambda w: Item(**w), reversed(work))):
        # if item.start.day != period_arrow.day:
        if item.start.full != period_arrow.full:
            if stop:
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

        log_entry: LogEntry = _log[item.name]
        log_entry.notes.extend(item.notes)
        log_entry.tags = item.tags

        log_entry.times.append(Timespan(item.start, item.end))

        if item.end:
            log_entry.duration += item.end - item.start
        else:
            log_entry.duration += _now - item.start
            current = item.name

    # Get total duration and make it pretty
    name_col_len = 0
    total_secs = 0
    for name, log_entry in _log.items():
        name_col_len = max(name_col_len, len(c.strip_color(name)), 24)

        duration = int(log_entry.duration.total_seconds())
        total_secs += duration
        pretty = secs2human(duration)
        log_entry.pretty = pretty

    title = c.b(c.w255(period_arrow.full))
    ago = arrows2rel_time(_now, period_arrow)
    if ago:
        title += f' {c.dim("| " + arrows2rel_time(_now, period_arrow))}'
    # if len(period) > 2:
    #     title = period.title()
    # else:
    #     title = f"{period[0]} {times.ABBREVS[period[1]]} ago"
    print(title + '\n' if detailed else '')

    # rprint(f"[b bright_white]{title}'s logs:[/]" + arrows2rel_time(_now, period_arrow) + '\n' if detailed else '')
    if groupby:
        for _tag, names in by_tag.items():
            print(c.tag(_tag))
            # print(f"\x1b[38;2;204;120;50m{_tag}\x1b[39m")
            for name in names:
                print_log(name, _log[name], current, detailed, name_col_len)
        return

    for name, item in sorted(_log.items(),
                                 key=lambda name_logentry_pair:
                             min(map(lambda timespan: timespan.start, name_logentry_pair[1].times))):
        print_log(name, item, current, detailed, name_col_len)

    rprint(f"[b bright_white]Total:[/] {secs2human(total_secs)}")


def print_log(name: str, log_entry:LogEntry, current: str, detailed: bool, name_col_len: int):
    if detailed:
        time = "\n  \x1b[2m"
        if log_entry.notes:
            time += '\n  ' + c.grey1('Times')

        for start, end in log_entry.times:
            if end:
                time += f'\n  {start.strftime("%X")} → {end.strftime("%X")} ({end - start})'
            else:
                time += f'\n  {start.strftime("%X")}'

        if log_entry.notes:
            time += '\n\n  ' + c.grey1('Notes')

        # for note_time, note_content in sorted(log_entry.notes, key=lambda _n: _n[0] if _n[0] else '0'):
        for note_time, note_content in dropwhile(lambda _n: not _n[0], log_entry.notes):
            if note_time:
                time += f'\n  {note_time}: {note_content}'
            else:
                time += f'\n  {note_content}'

        time += "\x1b[0m\n"
    else:
        first_start_time = min(map(lambda t: t[0], log_entry.times))
        time = c.dim('started: ' + first_start_time.strftime("%X"))

    if current == name:
        name = c.b(c.w255(name))
    else:
        name = c.w200(name)

    if detailed:
        tags = [c.dim(c.tag2(_tag)) for _tag in log_entry.tags]
        name += f'  {", ".join(tags)}'

    print(c.ljust_with_color(name, name_col_len),
          '\x1b[2m\t\x1b[0m ',
          log_entry.pretty,
          time)
