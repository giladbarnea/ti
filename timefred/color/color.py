import re


def rgb(s, _r, _g=None, _b=None):
    if not _g:
        _g = _r
        _b = _r
    return f'\x1b[38;2;{_r};{_g};{_b}m{s}\x1b[39m'


def bgrgb(s, _r, _g=None, _b=None):
    if not _g:
        _g = _r
        _b = _r
    return f'\x1b[48;2;{_r};{_g};{_b}m{s}\x1b[49m'


def activity(s):
    """Cool blue"""
    return b(rgb(s, 58, 150, 221))


def note(s):
    """Light pink/purple"""
    return rgb(s, 173, 127, 168)


def time(s):
    """Bright green"""
    return b(rgb(s, 138, 226, 52))


def digit(s):
    """Bright cyan"""
    return b(rgb(s, 52, 226, 226))


def tag(s):
    """Orangeish"""
    return b(rgb(s, 204, 120, 50))


def tag2(s):
    """Dim Orangeish"""
    return rgb(s, 160, 94, 40)


def title(s):
    return b(w255(s))


def grey150(s):
    return rgb(s, 150)


def grey100(s):
    return rgb(s, 100)


def fg(s, code):
    return f'\x1b[{code}m{s}\x1b[39m'


def w255(s):
    return fg(s, '97')


def w200(s):
    return rgb(s, 200)


def red(s):
    return fg(s, 31)


def green(s):
    return fg(s, 32)


def yellow(s):
    return fg(s, 33)


def blue(s):
    return fg(s, 34)


def orange(s):
    return rgb(s, 212, 122, 53)


def b(s):
    return f'\x1b[1m{s}\x1b[22m'


def dim(s):
    return f'\x1b[2m{s}\x1b[22m'


def i(s):
    return f'\x1b[3m{s}\x1b[23m'


COLOR_RE = re.compile("(\x1B\\[)[0-?]*[ -/]*[@-~]")


def strip_color(s):
    """Strip color from string."""
    rv = COLOR_RE.sub("", s)
    return rv


def len_color(s):
    """Length of color escape chars"""
    return len(s) - len(strip_color(s))


def ljust_with_color(s: str, width):
    """ljust string that might contain color."""
    return s.ljust(width + len_color(s))
