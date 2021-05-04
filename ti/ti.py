# coding: utf-8

"""
ti is a simple and extensible time tracker for the command line. Visit the
project page (http://ti.sharats.me) for more details.

Usage:
  ti (o|on) <name> [<start time>...]
  ti (f|fin) [<end time>...]
  ti (s|status)
  ti (t|tag) <tag>...
    Add tag to current activity, e.g `ti tag red for-joe`.
  ti (n|note) <note-text>...
    `ti note Discuss this with the other team.`
  ti (l|log) [today]
  ti (e|edit)
  ti (i|interrupt)
    Marks end time of current activity, pushes it to interrupt stack, and starts an "interrupt" activity.
  ti --no-color
  ti -h | --help

Options:
  -h --help         Show this help.
  <start-time>...   A time specification (goto http://ti.sharats.me for more on
                    this).
  <tag>...          Tags can be made of any characters, but its probably a good
                    idea to avoid whitespace.
  <note-text>...    Some arbitrary text to be added as `notes` to the currently
                    working project.
"""

import os
import subprocess
import sys
import tempfile
from contextlib import suppress
from datetime import datetime

import yaml
from rich import print as rprint

from ti import color as c
from ti.error import TIError, NoEditor, InvalidYAML, NoTask, BadArguments
from ti.store import store
from ti.times import formatted2arrow, timegap, human2formatted, reformat, now
from ti.action import log


def on(name, time="now", _tag=None):
    data = store.load()
    work = data['work']

    if work and 'end' not in (current := work[-1]):
        if current['name'] == name:
            rprint(f'Already working on {c.task(name)} since {reformat(current["start"], "HH:mm:ss")} ;)')
            return True
        ok = fin(time)
        if ok:
            return on(name, time, _tag)
        return False

    entry = {
        'name':  name,
        'start': time,
        }

    if _tag:
        entry.update({'tags': [_tag]})

    work.append(entry)
    store.dump(data)

    message = f'{c.green("Started")} working on {c.task(name)} at {reformat(time, "HH:mm:ss")}'
    if _tag:
        message += f". tag: {c.tag(_tag)}"
    rprint(message)


def fin(time, back_from_interrupt=True):
    ensure_working()

    data = store.load()

    current = data['work'][-1]
    current['end'] = time
    ok = store.dump(data)
    rprint(f'{c.yellow("Stopped")} working on {c.task(current["name"])} at {reformat(time, "HH:mm:ss")}')
    if not ok:
        return False
    if back_from_interrupt and len(data['interrupt_stack']) > 0:
        name = data['interrupt_stack'].pop()['name']
        store.dump(data)
        on(name, time)
        if len(data['interrupt_stack']) > 0:
            print('You are now %d deep in interrupts.'
                  % len(data['interrupt_stack']))
        else:
            print("Congrats, you're out of interrupts!")
    return True


def interrupt(name, time):
    ensure_working()

    fin(time, back_from_interrupt=False)

    data = store.load()
    if 'interrupt_stack' not in data:
        data['interrupt_stack'] = []
    interrupt_stack = data['interrupt_stack']

    interrupted = data['work'][-1]
    interrupt_stack.append(interrupted)
    store.dump(data)

    on('interrupt: ' + c.green(name), time)
    print('You are now %d deep in interrupts.' % len(interrupt_stack))


def note(content, time="now"):
    # ensure_working()
    formatted_time = human2formatted(time, fmt="HH:mm:ss")
    content = content.strip() + f' ({formatted_time})'
    data = store.load()
    current = data['work'][-1]

    if 'notes' not in current:
        current['notes'] = [content]
    else:
        current['notes'].append(content)

    store.dump(data)

    print(f'Noted {c.b(c.rgb(content,95,135,89))} to {c.b(c.rgb(current["name"], 58,150,221))}')


def tag(_tag):
    ensure_working()

    data = store.load()
    current = data['work'][-1]

    current_tags = list(current.get('tags', []))
    if _tag.lower() in [t.lower() for t in current_tags]:
        rprint(f'{c.task(current["name"])} already has tag {c.tag(_tag)}.')
        return
    current_tags.append(_tag)
    current['tags'] = current_tags

    store.dump(data)

    rprint(f"Okay, tagged {c.task(current['name'])} with {c.tag(_tag)}.")


def status(show_notes=False):
    ensure_working()

    data = store.load()
    current = data['work'][-1]

    start_time = formatted2arrow(current['start'])
    diff = timegap(start_time, now())

    notes = current.get('notes')
    if not show_notes or not notes:
        rprint(f'You have been working on {c.task(current["name"])} for {c.green(diff)}.')
        return

    rprint('\n    '.join([f'You have been working on {c.task(current["name"])} for {c.green(diff)}.\nNotes:[rgb(170,170,170)]',
                          *[f'[rgb(100,100,100)]o[/rgb(100,100,100)] {n}' for n in notes],
                          '[/]']))


def edit():
    if "EDITOR" not in os.environ:
        raise NoEditor("Please set the 'EDITOR' environment variable")

    data = store.load()
    yml = yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)

    cmd = os.getenv('EDITOR')
    fd, temp_path = tempfile.mkstemp(prefix='ti.')
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


def is_working():
    data = store.load()
    return data.get('work') and 'end' not in data['work'][-1]


def ensure_working():
    if is_working():
        return

    raise NoTask("For all I know, you aren't working on anything.")


def parse_args(argv=sys.argv):
    if len(argv) == 1:
        return log, {'detailed': True}
    if argv[1] == '-':
        return log, {}

    head = argv[1]
    tail = argv[2:]

    if head in ('-h', '--help', 'h', 'help'):
        raise BadArguments()

    elif head in ('e', 'edit'):
        fn = edit
        args = {}

    elif head in ('o', 'on'):
        if not tail:
            raise BadArguments("Need the name of whatever you are working on.")

        fn = on
        name = tail.pop(0)
        _tag = None
        if tail:
            with suppress(ValueError):
                _tag_idx = tail.index('-t')
                _tag = tail[_tag_idx + 1]
                tail = tail[:_tag_idx]
            time = human2formatted(' '.join(tail) if tail else 'now')
        else:
            time = human2formatted()
        args = {
            'name': name,
            'time': time,
            '_tag': _tag
            }

    elif head in ('f', 'fin'):
        fn = fin
        args = {'time': human2formatted(' '.join(tail) if tail else 'now')}

    elif head in ('s', 's+', 'status', 'status+'):
        fn = status
        args = {'show_notes': '+' in head}

    elif head in ('l', 'l-', 'log', 'log-'):
        fn = log
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

    elif head in ('t', 'tag'):
        if not tail:
            raise BadArguments("Please provide a tag.")

        fn = tag
        args = {'_tag': ' '.join(tail)}

    elif head in ('n', 'note'):
        if not tail:
            raise BadArguments("Please provide some text to be noted.")

        fn = note
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

    elif head in ('i', 'interrupt'):
        if not tail:
            raise BadArguments("Need the name of whatever you are working on.")

        fn = interrupt
        name = tail.pop(0)
        args = {
            'name': name,
            'time': human2formatted(' '.join(tail) if tail else 'now'),
            }

    else:
        raise BadArguments("I don't understand %r" % (head,))

    return fn, args


def main():
    try:
        fn, args = parse_args()
        fn(**args)
    except TIError as e:
        msg = str(e) if len(str(e)) > 0 else __doc__
        print(msg, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
