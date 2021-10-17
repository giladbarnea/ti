import re

from timefred import color as c

NONWORD_RE = re.compile(r'[\W_]')


def confirm(question):
    return input(f' {c.blue("?")} ' + question + c.b(' [y/n]  ')).lower() in ('y', 'yes')


def normalize_str(s):
    # if hasattr(s, '__normalized__'):
    #     return s
    # normalized = NONWORD_RE.sub('', s.lower().strip())
    # normalized.__normalized__ = True
    # return normalized
    return NONWORD_RE.sub('', s.lower().strip())


from time import perf_counter_ns


def timeit(function):
    def decorator(*args, **kwargs):
        a = perf_counter_ns()
        try:
            rv = function(*args, **kwargs)
            return rv
        finally:
            b = perf_counter_ns()
            print(f'{function.__qualname__}({", ".join(map(str,args)) + ", " if args else ""}{", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())}) took {round((b - a) / 1000, 2):,} μs ({round((b - a) / 1_000_000, 1):,} ms)')

    return decorator
