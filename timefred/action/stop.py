from timefred import color as c
from timefred.space import DefaultAttrDictSpace
from timefred.store import store, Entry
from timefred.time import XArrow
from timefred.util import confirm


def stop(end: XArrow) -> bool:
    # ensure_working()
    
    work: DefaultAttrDictSpace = store.load()
    
    # TODO: work[day].stop(end). Consider moving .ongoing_activity() to work level because mightve started yesterday
    item = Entry(**data[-1])
    
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
