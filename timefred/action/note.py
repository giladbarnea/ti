from timefred import color as c
from timefred.error import BadTime
from timefred.store import store, Entry
from timefred.time import XArrow
from timefred.util import confirm


def note(content, time="now"):
    time = XArrow.from_human(time)
    # time = human2arrow(time)
    if time > XArrow.now():
        raise BadTime(f"in the future: {time}")
    content_and_time = content.strip() + f' ({time.HHmmss})'
    work = store.load()
    idx = -1
    item = Entry(**work[idx])
    if time < item.start:
        # Note for something in the past
        idx, item_in_range = next((i, item) for i, item in enumerate(map(lambda w: Entry(**w), reversed(work)), 1) if item.start.full == time.full)
        idx *= -1
        
        if item_in_range.name == item.name:
            item = item_in_range
        else:
            if not confirm(f'{item.name_colored} started only at {c.time(item.start.strftime("%X"))},\n'
                           f'note to {item_in_range.name_colored} (started at {c.time(item_in_range.start.strftime("%X"))})?'):
                return
            item = item_in_range
    
    for n in item.notes:
        if n.is_similar(content):
            if not confirm(f'{item.name_colored} already has this note: {c.b(c.note(n))}.\n'
                           'Add anyway?'):
                return
    
    item.notes.append(content_and_time)
    work[idx]['notes'] = item.notes
    store.dump(work)
    
    print(f'Noted {c.b(c.note(content_and_time))} to {item.name_colored}')
