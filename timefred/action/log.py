import re
from collections import defaultdict
from typing import Literal, Union

from timefred import color as c
from timefred.store import store, Entry, Activity
from timefred.time.timeutils import arrows2rel_time
from timefred.time.xarrow import XArrow


# @break_on_exc
def log(time: Union[str, XArrow] = "today",
        *,
        detailed=True,
        groupby: Literal['t', 'tag'] = None) -> bool:
    if groupby and groupby not in ('t', 'tag'):
        raise ValueError(f"log({time = !r}, {detailed = }, {groupby = !r}) groupby must be either 't' | 'tag'")
    work = store.load()
    if not work:
        return False
    current = None
    arrow = XArrow.from_human(time)
    # now = arrow.now() # TODO: should support a range of times, spanning several days etc
    day = work[arrow.DDMMYY]
    if not day:
        return False
    # _log = Log()
    activities: list[Activity] = day.values()
    activity: Activity = activities[0]
    entry: Entry = activity[0]
    entry_timespan = entry.timespan
    print(f'{entry_timespan = !r}')
    by_tag = defaultdict(set)  # activities = list(day.values());
    # for i, entry in enumerate(reversed(work)):
    # for day_key in reversed(work):
    # day: Day = work[day_key]
    # # day
    # # item = Entry(**entry)
    # # for i, item in enumerate(map(lambda w: Entry(**w), reversed(work))):
    # item_start = item.start
    # item_start_DDMMYY = item_start.DDMMYY
    # period_arrow_DDMMYY = period_arrow.DDMMYY
    # if item_start_DDMMYY != period_arrow_DDMMYY:
    # if period_arrow > item.start:
    # # We have iterated past period
    # break
    # continue
    # if period_arrow.month != item.start.month and period_arrow.year != item.start.year:
    # break
    # # noinspection PyUnreachableCode
    # if groupby and groupby in ('t', 'tag'):
    # if not tags:
    # by_tag[None].add(name)
    # else:
    # for t in tags:
    # by_tag[t].add(name)
    # log_entry = _log[item.name]
    # log_entry.name = item.name
    # item_notes = item.notes
    # log_entry_notes = log_entry.notes
    # log_entry_notes.extend(item_notes)
    # log_entry.tags |= item.tags
    # timespan = Timespan(item.start, item.end or now)
    # log_entry.timespans.append(timespan)
    # if not timespan.end:
    # log_entry.is_current = True
    
    title = c.title(arrow.full)
    now = XArrow.now()
    arrow.humanize()
    ago = arrows2rel_time(now, arrow)
    if ago:
        title += f' {c.dim("| " + ago)}'
    
    print(title + '\n')
    # if not _log:
    #     return True
    name_column_width = max(*map(len, map(lambda _: _.name, activities)), 24)
    if groupby:
        for _tag, names in by_tag.items():
            print(c.tag(_tag))
            for name in names:
                print_log(name, _log[name], current, detailed, name_column_width)
        return True
    
    # for name, log_entry in _log.sorted_entries():
    for activity in activities:
        print(activity.pretty(detailed, name_column_width))
    
    print(c.title('Total: ') + re.sub(r'\d', lambda match: f'{c.digit(match.group())}', day.human_duration()))
    print()