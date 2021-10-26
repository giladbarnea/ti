from timefred import color as c
from timefred.store import store, Entry
from timefred.time import Timespan, XArrow
from timefred.action.util import ensure_working


def status(show_notes=False):
    ensure_working()
    
    data = store.load()
    current = Entry(**data[-1])
    duration = Timespan(current.start, XArrow.now()).human_duration()
    # diff = timegap(current.start, now())
    
    # notes = current.get('notes')
    if not show_notes or not current.notes:
        print(f'You have been working on {current.name.colored} for {c.time(duration)}.')
        return
    
    print('\n    '.join([f'You have been working on {current.name_colored} for {c.time(duration)}.\nNotes:',  # [rgb(170,170,170)]
                         *[f'{c.grey100("o")} {n.pretty()}' for n in current.notes]
                         ]))
