from typing import Union

from timefred import color as c
# from timefred.color import Colored
from timefred.note import Note
from timefred.store import store, Activity, Entry
from timefred.time import XArrow
from timefred.action import stop


def on(name: str, time: Union[str, XArrow], tag=None, note=None):
    work = store.load()
    if work:
        day = work[time.DDMMYY]
        activity = day[name]
        if activity.ongoing() and activity.has_similar_name(name):
            print(f'{c.orange("Already")} working on {activity.name.colored} since {c.time(activity.start.DDMMYYHHmmss)} ;)')
            return True
        ok = stop(time)
        if ok:
            return on(name, time, tag)
        breakpoint()
        return False
    
    entry = Entry(start=time)
    # assert entry
    # assert entry.start
    # assert isinstance(entry.start, XArrow)
    
    activity = Activity(name=name)
    # assert not activity
    # assert len(activity) == 0
    # assert activity.name == 'Got to office', f"activity.name is not 'Got to office' but rather {activity.name!r}"
    # assert isinstance(activity.name, Colored), f'Not Colored, but rather {type(activity.name)}'
    activity.append(entry)
    # assert len(activity) == 1
    if tag:
        entry.tags.add(tag)
    
    if note:
        note = Note(note, time)
        entry.notes.append(note)
    
    # work[entry.start.DDMMYY].append({str(activity.name): activity.dict(exclude=('timespan', 'name'))})
    day = work[entry.start.DDMMYY]
    day[str(activity.name)] = activity
    # work[activity.start.DDMMYY].append(activity)
    # work.append(activity.dict())
    ok = store.dump(work)
    if not ok:
        breakpoint()
    
    # message = f'{c.green("Started")} working on {activity.name_colored} at {c.time(reformat(time, timeutils.FORMATS.date_time))}'
    message = f'{c.green("Started")} working on {activity.name.colored} at {c.time(entry.start.DDMMYYHHmmss)}'
    if tag:
        message += f". Tag: {c.tag(tag)}"
    
    if note:
        message += f". Note: {note.pretty()}"
    print(message)
