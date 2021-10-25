from timefred.error import NoTask
from timefred.store import store


def is_working() -> bool:
    data = store.load()
    return data and 'end' not in data[-1]


def ensure_working():
    if is_working():
        return
    
    raise NoTask("For all I know, you aren't working on anything.")
