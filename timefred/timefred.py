# coding: utf-8
"""
Timefred is a beautiful and intelligent time tracker for the command line. Visit the
project page (https://github.com/giladbarnea/timefred) for more details.

Usage:
  tf (o|on) <name> [start time = "now"]
  tf (f|fin) [end time = "now"]
  tf (s|status)[+]
  tf (t|tag) <tag> [time = "now"]
    Add tag to current activity, e.g `tf tag research`.
  tf (n|note) <note-text> [time = "now"]
    tf note Discuss this with the other team.
  tf (l|log) [period = "today"]
  tf (e|edit)
  tf (a|agg|aggregate)
  tf (i|interrupt)
    Marks end time of current activity, pushes it to interrupt stack, and starts an "interrupt" activity.
  tf --no-color
  tf -h | --help

Options:
  -h --help         Show this help.
  <start-time>...   A time specification (goto https://github.com/giladbarnea/timefred for more on
                    this).
  <tag>...          Tags can be made of any characters, but its probably a good
                    idea to avoid whitespace.
  <note-text>...    Some arbitrary text to be added as `notes` to the currently
                    working project.
"""
import debug

import os
import subprocess
import sys
import tempfile
from contextlib import suppress
from typing import Callable, Tuple, List

import yaml

from timefred import color as c, util
from timefred._dev import generate_completion
from timefred.action import log
from timefred.config import config
from timefred.error import TIError, NoEditor, InvalidYAML, NoTask, BadArguments, BadTime
from timefred.item import Item
from timefred.note import Note
from timefred.store import store
# from timefred.time.timespan import Timespan
from timefred.time import Timespan, XArrow, isoweekday
from timefred.util import confirm

FORMATS = config.time.formats
from pdbpp import break_on_exc


@break_on_exc
def on(name: str, time: XArrow, _tag=None, _note=None):
    work = store.load()

    if work and not (current := Item(**work[-1])).end:
        # Finish current, then start (recursively)
        if current.has_similar_name(name):
            # print(f'{c.orange("Already")} working on {current.name_colored} since {c.time(reformat(current["start"], timeutils.FORMATS.date_time))} ;)')
            print(f'{c.orange("Already")} working on {current.name_colored} since {c.time(current.start.DDMMYYHHmmss)} ;)')
            return True
        ok = fin(time)
        if ok:
            return on(name, time, _tag)
        breakpoint()
        return False

    item = Item(name, start=time)

    if _tag:
        item.tags.add(_tag)

    if _note:
        item.notes.append(Note(_note, time))

    work.append(item.dict())
    ok = store.dump(work)
    if not ok:
        breakpoint()

    # message = f'{c.green("Started")} working on {item.name_colored} at {c.time(reformat(time, timeutils.FORMATS.date_time))}'
    message = f'{c.green("Started")} working on {item.name_colored} at {c.time(item.start.DDMMYYHHmmss)}'
    if _tag:
        message += f". tag: {c.tag(_tag)}"

    if _note:
        message += f". note: {item.notes[-1].pretty()}"
    print(message)


def fin(end: XArrow) -> bool:
    ensure_working()

    data = store.load()

    item = Item(**data[-1])

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


# def interrupt(name, time):
# 	ensure_working()
#
# 	fin(time)
#
# 	data = store.load()
# 	if 'interrupt_stack' not in data:
# 		data['interrupt_stack'] = []
# 	interrupt_stack = data['interrupt_stack']
#
# 	interrupted = data['work'][-1]
# 	interrupt_stack.append(interrupted)
# 	store.dump(data)
#
# 	on('interrupt: ' + c.green(name), time)
# 	print('You are now %d deep in interrupts.' % len(interrupt_stack))


def note(content, time="now"):
    time = XArrow.from_human(time)
    # time = human2arrow(time)
    if time > XArrow.now():
        raise BadTime(f"in the future: {time}")
    content_and_time = content.strip() + f' ({time.HHmmss})'
    work = store.load()
    idx = -1
    item = Item(**work[idx])
    if time < item.start:
        # Note for something in the past
        idx, item_in_range = next((i, item) for i, item in enumerate(map(lambda w: Item(**w), reversed(work)), 1) if item.start.full == time.full)
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


def tag(_tag, time="now") -> bool:
    time = XArrow.from_human(time)
    # time = human2arrow(time)
    if time > time.now():
        raise BadTime(f"in the future: {time}")
    work = store.load()
    idx = -1
    item = Item(**work[idx])
    if time < item.start:
        # Tag something in the past
        idx = -1 * next(i for i, work in enumerate(reversed(work), 1) if Item(**work).start <= time)
        item_in_range = Item(**work[idx])
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


def status(show_notes=False):
    ensure_working()

    data = store.load()
    current = Item(**data[-1])
    duration = Timespan(current.start, XArrow.now()).human_duration()
    # diff = timegap(current.start, now())

    # notes = current.get('notes')
    if not show_notes or not current.notes:
        print(f'You have been working on {current.name_colored} for {c.time(duration)}.')
        return

    print('\n    '.join([f'You have been working on {current.name_colored} for {c.time(duration)}.\nNotes:',  # [rgb(170,170,170)]
                         *[f'{c.grey100("o")} {n.pretty()}' for n in current.notes]
                         ]))


def edit():
    if "EDITOR" not in os.environ:
        raise NoEditor("Please set the 'EDITOR' environment variable")

    data = store.load()
    yml = yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)

    cmd = os.getenv('EDITOR')
    fd, temp_path = tempfile.mkstemp(prefix='timefred.')
    with open(temp_path, "r+") as f:
        f.write(yml.replace('\n- ', '\n\n- '))
        f.seek(0)
        subprocess.check_call(cmd + ' ' + temp_path, shell=True)
        yml = f.read()
        f.truncate()

    os.close(fd)
    os.remove(temp_path)

    try:
        data = yaml.load(yml)
    except:
        raise InvalidYAML("Oops, that YAML doesn't appear to be valid!")

    store.dump(data)


def is_working() -> bool:
    data = store.load()
    return data and 'end' not in data[-1]


def ensure_working():
    if is_working():
        return

    raise NoTask("For all I know, you aren't working on anything.")


def parse_args(argv=[]) -> Tuple[Callable, dict]:
    if not argv:
        argv = sys.argv
    # *** log
    # ** timefred [-]
    # timefred -> log(detailed=True)
    # timefred - -> log()
    argv_len = len(argv)
    if argv_len == 1:
        return log, {'detailed': True}
    if argv[1] == '-':
        return log, {'detailed': False}

    # ** timefred thursday
    if len(argv[1]) > 1:
        if argv[1].lower() == 'yesterday':
            return log, {'period': argv[1], 'detailed': True}
        with suppress(ValueError):
            isoweekday(argv[1])
            return log, {'period': argv[1], 'detailed': True}

    head = argv[1]
    tail: List[str] = argv[2:]

    # ** log
    if head in ('l', 'l-', 'log', 'log-'):
        groupby = None
        with suppress(ValueError, AttributeError):
            groupby_idx = tail.index('-g')
            groupby = tail[groupby_idx + 1]
            tail = tail[:groupby_idx]
        if tail:
            period = ' '.join(tail)
        else:
            period = 'today'
        args = {
            'period':   period,
            'detailed': '-' not in head,
            'groupby':  groupby
            }
        return log, args

    # *** help
    if 'help' in head or head in ('-h', 'h'):
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    # *** edit
    elif head in ('e', 'edit'):
        return edit, {}

    # *** on
    elif head in ('o', 'on'):
        if not tail:
            raise BadArguments("Need the name of whatever you are working on.")

        name = tail.pop(0)
        _tag = None
        _note = None
        if tail:
            with suppress(ValueError):
                _tag_idx = tail.index('-t')
                _tag = tail[_tag_idx + 1]
                tail = tail[:_tag_idx]
            with suppress(ValueError):
                _note_idx = tail.index('-n')
                _note = tail[_note_idx + 1]
                tail = tail[:_note_idx]
            # time = human2formatted(' '.join(tail) if tail else 'now')
            time = XArrow.from_human(' '.join(tail) if tail else 'now')
        else:
            # time = human2formatted()
            time = XArrow.now()
        args = {
            'name':  name,
            'time':  time,
            '_tag':  _tag,
            '_note': _note
            }
        return on, args

    # *** fin
    elif head in ('f', 'fin'):
        args = {
            'time': XArrow.from_human(' '.join(tail) if tail else 'now')
            }
        return fin, args

    # *** status
    elif head in ('s', 's+', 'status', 'status+'):
        args = {'show_notes': '+' in head}
        return status, args



    # *** tag
    elif head in ('t', 'tag'):
        if not tail:
            raise BadArguments("Please provide a tag.")

        if len(tail) == 2:
            _tag, time = tail
            args = {
                '_tag': _tag,
                'time': time
                }
        elif len(tail) == 1:
            args = {'_tag': tail[0]}
        else:
            args = {'_tag': ' '.join(tail)}
        return tag, args

    # *** note
    elif head in ('n', 'note'):
        if not tail:
            raise BadArguments("Please provide some text to be noted.")

        if len(tail) == 2:
            content, time = tail
            args = {
                'content': content,
                'time':    time
                }
        elif len(tail) == 1:
            args = {'content': tail[0]}
        else:
            args = {'content': ' '.join(tail)}
        return note, args

    # *** interrupt
    # elif head in ('i', 'interrupt'):
    # 	if not tail:
    # 		raise BadArguments("Need the name of whatever you are working on.")
    #
    # 	name = tail.pop(0)
    # 	args = {
    # 		'name': name,
    # 		'time': human2formatted(' '.join(tail) if tail else 'now'),
    # 		}
    # 	return interrupt, args

    # *** aggregate
    elif head in ('a', 'ag', 'agg', 'aggreg', 'aggregate'):
        if not tail:
            raise BadArguments("Need at least <start> <stop>")
        if len(tail) == 1:
            times = tail[0]
            if '-' in times:
                start, stop = map(str.strip, times.partition('-'))
            elif ' ' in times:
                start, stop = map(str.strip, times.partition(' '))
            else:
                raise BadArguments("Need at least <start> <stop>")
        else:
            start, stop, *tail = tail
        # start_arw = human2arrow(start)
        # stop_arw = human2arrow(stop)
        start_arw = XArrow.from_human(start)
        stop_arw = XArrow.from_human(stop)
        breakpoint()

    # *** _dev
    if head == '_dev':
        if tail[0] == 'generate completion':
            return generate_completion, {}

    raise BadArguments("I don't understand %r" % (head,))


def main(argv=[]):
    try:
        fn, args = parse_args([__name__, *argv] if argv else None)
        fn(**args)
    except TIError as e:
        msg = str(e) if len(str(e)) > 0 else __doc__
        print(msg, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
