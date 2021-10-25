from timefred import color as c, util
from timefred.error import BadTime
from timefred.store import store, Entry
from timefred.time import XArrow
from timefred.util import confirm


def tag(_tag, time="now") -> bool:
    time = XArrow.from_human(time)
    # time = human2arrow(time)
    if time > time.now():
        raise BadTime(f"in the future: {time}")
    work = store.load()
    idx = -1
    item = Entry(**work[idx])
    if time < item.start:
        # Tag something in the past
        idx = -1 * next(i for i, work in enumerate(reversed(work), 1) if Entry(**work).start <= time)
        item_in_range = Entry(**work[idx])
        if not confirm(f'{item.name_colored} started only at {c.time(item.start.strftime("%X"))}, '
                       f'Tag {item_in_range.name_colored} (started at {c.time(item_in_range.start.strftime("%X"))})?'):
            return False
        item = item_in_range
    tag_colored = c.tag(_tag)
    if any(util.normalize_str(_tag) == t for t in map(util.normalize_str, item.tags)):
        print(f'{item.name_colored} already has tag {tag_colored}.')
        return False
    item.tags.add(_tag)
    work[idx]['tags'] = item.tags
    
    ok = store.dump(work)
    if ok:
        print(f"Okay, tagged {item.name_colored} with {tag_colored}.")
    else:
        print(f"Failed writing to sheet")
    return ok
