import re
from collections import defaultdict
from datetime import timedelta, datetime
from typing import List, Tuple, Literal

# from loguru import logger
from rich import print as rprint

from ti import color as c, times
# from ti.item import Item
from ti.store import store
from ti.times import human2arrow, formatted2arrow, secs2human, now, arrows2rel_time

note_time_re = re.compile(r'(.+) \(([\d/:]+)\)', re.IGNORECASE)


# @logger.catch()
def log(period="today", *, detailed=False, groupby: Literal['t', 'tag'] = None):
    if groupby and groupby not in ('t', 'tag'):
        raise ValueError(f"log({period = }, {groupby = }) groupby must be either 't' | 'tag'")
    data = store.load()
    work = data['work'] + data['interrupt_stack']
    _log = defaultdict(lambda: {'duration': timedelta(), 'times': [], 'notes': []})
    current = None
    period_arrow = human2arrow(period)
    _now = now()

    # None key contains items with no tags
    by_tag = defaultdict(set)
    # stop = False
    # for i, item in enumerate(map(lambda w: Item(**w), reversed(work))):
    # 	if item.start.day != period_arrow.day:
    # 		if stop:
    # 			break
    # 	else:
    # 		for note in item.notes:
    # 			match = note_time_re.fullmatch(note)
    # 			if match:
    # 				match_groups = match.groups()
    # 				note_content = match_groups[0]
    # 				note_time = match_groups[1]
    # 				# _log[item.name]['notes'].append((note_time, note_content))
    # 			else:
    # 				...
    # 				# _log[item.name]['notes'].append(note)
    # 		stop = True

    for item in work:
        start_time = formatted2arrow(item['start'])
        if period and period_arrow.day != start_time.day:
            continue
        end_time = item.get('end') and formatted2arrow(item['end'])
        name = item['name']
        tags = item.get('tags', set())
        if groupby and groupby in ('t', 'tag'):
            if not tags:
                by_tag[None].add(name)
            else:
                for t in tags:
                    by_tag[t].add(name)
        for note in item.get('notes', set()):
            match = note_time_re.fullmatch(note)
            if match:
                match_groups = match.groups()
                note_content = match_groups[0]
                note_time = match_groups[1]
                _log[name]['notes'].append((note_time, note_content))
            else:
                _log[name]['notes'].append(note)

        _log[name]['tags'] = tags

        _log[name]['times'].append((start_time, end_time))

        if end_time:
            _log[name]['duration'] += end_time - start_time
        else:
            _log[name]['duration'] += _now - start_time
            current = name

    # Get total duration and make it pretty
    name_col_len = 0
    total_secs = 0
    for name, item in _log.items():
        name_col_len = max(name_col_len, len(c.strip_color(name)), 24)

        secs = int(item['duration'].total_seconds())
        total_secs += secs
        pretty = secs2human(secs)
        _log[name]['pretty'] = pretty

    title = c.b(c.w255(period_arrow.strftime('%A %x')))
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

    for name, item in sorted(_log.items(), key=lambda entry: min(map(lambda _t: _t[0], entry[1]['times']))):
        print_log(name, item, current, detailed, name_col_len)

    rprint(f"[b bright_white]Total:[/] {secs2human(total_secs)}")


def print_log(name: str, item, current: str, detailed: bool, name_col_len: int):
    if detailed:
        start_end_times: List[Tuple[datetime, datetime]] = item["times"]
        time = "\n  \x1b[2m"
        if item["notes"]:
            time += '\n  ' + c.grey1('Times')
            # time += f"\n  \x1b[38;2;150;150;150mTimes\x1b[0;2m"
        for start, end in start_end_times:
            if end:
                time += f'\n  {start.strftime("%X")} → {end.strftime("%X")} ({end - start})'
            else:
                time += f'\n  {start.strftime("%X")}'

        if item["notes"]:
            time += '\n\n  ' + c.grey1('Notes')
            # time += '\n\n  \x1b[38;2;150;150;150mNotes\x1b[0;2m'
        for note_time, note_content in sorted(item["notes"], key=lambda _n: _n[0]):
            time += f'\n  {note_time}: {note_content}'
        time += "\x1b[0m\n"
    else:
        first_start_time = min(map(lambda t: t[0], item["times"]))
        time = c.dim('started: ' + first_start_time.strftime("%X"))
        # time = f' \x1b[2mstarted: {first_start_time.strftime("%X")}\x1b[0m'

    if current == name:
        name = c.b(c.w255(name))
        # name = f'\x1b[1;38;2;255;255;255m{name}\x1b[0m'
    else:
       # name = c.rgb(name, 200)
       name = c.w200(name)

    if detailed:
        tags = [c.dim(c.tag2(_tag)) for _tag in item["tags"]]
        # tags = [f"\x1b[2;38;2;204;120;50m{_tag}\x1b[22;39m" for _tag in item["tags"]]
        name += f'  {", ".join(tags)}'

    print(c.ljust_with_color(name, name_col_len),
          '\x1b[2m\t\x1b[0m ',
          item['pretty'],
          time)
