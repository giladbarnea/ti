from timefred import util, color as c
from timefred.note import Note
from timefred.store import store, Entry, Work
from timefred.tag import Tag
from timefred.time import XArrow


def stop(end: XArrow, tag: Tag = None, note: Note = None) -> bool:
    # ensure_working()
    
    work: Work = store.load()
    ongoing_activity = work.ongoing_activity()
    entry = ongoing_activity.stop(end, tag, note)
    
    if entry.start.day < end.day:
        if not util.confirm(f'{ongoing_activity.name} started on {c.time(entry.start.DDMMYYHHmmss)}, continue?'):
            return False
    
    data[-1]['end'] = end.DDMMYYHHmmss
    item.end = end
    ok = store.dump(data)
    print(f'{c.yellow("Stopped")} working on {item.name_colored} at {c.time(item.end.DDMMYYHHmmss)}. ok: {ok}')
    return ok
