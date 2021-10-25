from timefred import color as c
from timefred.note import Note
from timefred.store import store, Entry
from timefred.time import XArrow
from timefred.action import fin


def on(name: str, time: XArrow, _tag=None, _note=None):
    work = store.load()
    if work:
        first_entry = Entry.from_entry(work[next(iter(work))])
        if not first_entry.end:
            current = first_entry
            # Finish current, then start (recursively)
            if current.has_similar_name(name):
                # print(f'{c.orange("Already")} working on {current.name_colored} since {c.time(reformat(current["start"], timeutils.FORMATS.date_time))} ;)')
                print(f'{c.orange("Already")} working on {current.name.colored} since {c.time(current.start.DDMMYYHHmmss)} ;)')
                return True
            ok = fin(time)
            if ok:
                return on(name, time, _tag)
            breakpoint()
            return False

    item = Entry(name=name, start=time)
    
    if _tag:
        item.tags.add(_tag)
    
    if _note:
        item.notes.append(Note(_note, time))
    
    work[item.start.DDMMYY].append({str(item.name): item.dict(exclude=('timespan', 'name'))})
    # work[item.start.DDMMYY].append(item)
    # work.append(item.dict())
    ok = store.dump(work)
    if not ok:
        breakpoint()
    
    # message = f'{c.green("Started")} working on {item.name_colored} at {c.time(reformat(time, timeutils.FORMATS.date_time))}'
    message = f'{c.green("Started")} working on {item.name.colored} at {c.time(item.start.DDMMYYHHmmss)}'
    if _tag:
        message += f". Tag: {c.tag(_tag)}"
    
    if _note:
        message += f". Note: {item.notes[-1].pretty()}"
    print(message)
