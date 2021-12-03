from timefred import color as c
from timefred.note import Note
from timefred.store import store, Entry, Work
from timefred.tag import Tag
from timefred.time import XArrow
from timefred.util import confirm


def stop(end: XArrow, tag: Tag, note: Note) -> bool:
    # ensure_working()
    
    work: Work = store.load()
    ongoing_activity = work.ongoing_activity()
    entry = ongoing_activity.stop(end, tag, note)
    
    if item.start > end:
        print(f'{c.orange("Cannot")} finish {item.name_colored} at {c.time(end.DDMMYYHHmmss)} because it only started at {c.time(item.start.DDMMYYHHmmss)}.')
        return False
    if item.start.day < end.day:
        print(end)
        if not confirm(f'{item.name_colored} started on {c.time(item.start.DDMMYYHHmmss)}, continue?'):
            return False
    data[-1]['end'] = end.DDMMYYHHmmss
    item.end = end
    ok = store.dump(data)
    print(f'{c.yellow("Stopped")} working on {item.name_colored} at {c.time(item.end.DDMMYYHHmmss)}. ok: {ok}')
    return ok
