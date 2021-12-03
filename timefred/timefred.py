# coding: utf-8
"""
Timefred is a beautiful and intelligent time tracker for the command line. Visit the
project page (https://github.com/giladbarnea/timefred) for more details.

Usage:
  tf (o|on) <name> [start time = "now"]
  tf (f|stop) [end time = "now"]
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
import sys
from contextlib import suppress
from typing import Callable, Tuple, List

from timefred._dev import generate_completion
from timefred import action
# from timefred.action import log, note, edit, stop, on, status, tag
from timefred.config import config
from timefred.error import TIError, BadArguments
# from timefred.time.timespan import Timespan
from timefred.time import XArrow, isoweekday

FORMATS = config.time.formats


# def interrupt(name, time):
# 	ensure_working()
#
# 	stop(time)
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


def parse_args(argv=[]) -> Tuple[Callable, dict]:
    if not argv:
        argv = sys.argv
    # *** log
    # ** timefred
    # timefred -> log(detailed=True)
    argv_len = len(argv)
    if argv_len == 1:
        return action.log, {'detailed': True}
    
    # ** timefred thursday
    if len(argv[1]) > 1:
        if argv[1].lower() == 'yesterday':
            return action.log, {'period': argv[1], 'detailed': True}
        with suppress(ValueError):
            isoweekday(argv[1])
            return action.log, {'period': argv[1], 'detailed': True}
    
    head = argv[1]
    tail: list[str] = argv[2:]
    
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
        return action.log, args
    
    # *** help
    if 'help' in head or head in ('-h', 'h'):
        print(__doc__, file=sys.stderr)
        sys.exit(0)
    
    # *** edit
    elif head in ('e', 'edit'):
        return action.edit, {}
    
    # *** on
    elif head in ('+', 'o', 'on'):
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
            time = XArrow.from_human(' '.join(tail) if tail else 'now')
        else:
            time = XArrow.now()
        args = {
            'name': name,
            'time': time,
            'tag':  _tag,
            'note': _note
            }
        return action.on, args
    
    # *** stop
    elif head in ('-', 'stop'):
        args = {
            'time': XArrow.from_human(' '.join(tail) if tail else 'now')
            }
        return action.stop, args
    
    # *** status
    elif head in ('?', '??', 's', 's+', 'status', 'status+'):
        args = {'show_notes': '+' in head}
        return action.status, args
    
    
    
    # *** tag
    elif head in ('t', 'tag'):
        if not tail:
            raise BadArguments("Please provide a tag.")
        
        if len(tail) == 2:
            _tag, time = tail
            args = {
                'tag': _tag,
                'time': time
                }
        elif len(tail) == 1:
            args = {'tag': tail[0]}
        else:
            args = {'tag': ' '.join(tail)}
        return action.tag, args
    
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
        return action.note, args
    
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
