from collections import defaultdict
from datetime import timedelta, datetime
from typing import List, Tuple, Literal

from loguru import logger
from rich import print as rprint

from ti import color as c
from ti import times
from ti.store import store
from ti.times import human2dt, formatted2dt, secs2human


@logger.catch()
def log(period="today", *, detailed=False, groupby: Literal['t', 'tag'] = None):
    if groupby and groupby not in ('t', 'tag'):
        raise ValueError(f"log({period = }, {groupby = }) groupby must be either 't' | 'tag'")
    data = store.load()
    work = data['work'] + data['interrupt_stack']
    _log = defaultdict(lambda: {'duration': timedelta(), 'times': []})
    current = None
    period_dt = human2dt(period)
    if not period_dt:
        breakpoint()
    now = datetime.now()

    # None key contains items with no tags
    by_tag = defaultdict(set)
    for item in work:
        start_time = formatted2dt(item['start'])
        if period and period_dt.day != start_time.day:
            continue
        end_time = item.get('end') and formatted2dt(item['end'])
        name = item['name']
        tags = item.get('tags', set())
        if groupby and groupby in ('t', 'tag'):
            if not tags:
                by_tag[None].add(name)
            else:
                for t in tags:
                    by_tag[t].add(name)
        _log[name]['tags'] = tags

        _log[name]['times'].append((start_time, end_time))

        if end_time:
            _log[name]['duration'] += end_time - start_time
        else:
            _log[name]['duration'] += now - start_time
            current = name

    name_col_len = 0
    total_secs = 0
    for name, item in _log.items():
        name_col_len = max(name_col_len, len(c.strip_color(name)))

        secs = int(item['duration'].total_seconds())
        total_secs += secs
        pretty = secs2human(secs)
        _log[name]['pretty'] = pretty

    if len(period) > 2:
        title = period.title()
    else:
        title = f"{period[0]} {times.ABBREVS[period[1]]} ago"

    rprint(f"[b bright_white]{title}'s logs:[/]" + '\n' if detailed else '')
    if groupby:
        for _tag, names in by_tag.items():
            print(f"\x1b[38;2;204;120;50m{_tag}\x1b[39m")
            for name in names:
                print_log(name, _log[name], current, detailed, name_col_len)
        return
    for name, item in sorted(_log.items(), key=lambda entry: min(map(lambda _t: _t[0], entry[1]['times']))):
        print_log(name, item, current, detailed, name_col_len)

    rprint(f"[b bright_white]Total:[/] {secs2human(total_secs)}")


def print_log(name, item, current: str, detailed: bool, name_col_len: int):
    if detailed:
        start_end_times: List[Tuple[datetime, datetime]] = item["times"]
        time = "\n  \x1b[2m"
        for start, end in start_end_times:
            if end:
                time += f'\n  {start.strftime("%X")} → {end.strftime("%X")} ({end - start})'
            else:
                time += f'\n  {start.strftime("%X")}'
        time += "\x1b[0m\n"
    else:
        fist_start_time = min(map(lambda t: t[0], item["times"]))
        time = f' \x1b[2mstarted: {fist_start_time.strftime("%X")}\x1b[0m'

    if current == name:
        name = f'\x1b[1m{name}\x1b[0m'

    if detailed:
        tags = [f"\x1b[2;38;2;204;120;50m{_tag}\x1b[22;39m" for _tag in item["tags"]]
        name += f'  {", ".join(tags)}'

    print(c.ljust_with_color(name, name_col_len),
          '\x1b[2m∙ ∙\x1b[0m ',
          item['pretty'],
          time)
