import re


def rgb(s, r, g=None, b=None):
    if not g:
        g = r
        b = r
    return f'\x1b[38;2;{r};{g};{b}m{s}\x1b[39m'


def task(s):
    return b(rgb(s, 58, 150, 221))


def note(s):
    # Light pink/purupple
    return rgb(s, 173, 127, 168)


def time(s):
    # Bright green
    return b(rgb(s, 138, 226, 52))


def tag(s):
    # Orangeish
    return rgb(s, 204, 120, 50)


def tag2(s):
    # Dim Orangeish
    return rgb(s, 160, 94, 40)


def grey1(s):
    return rgb(s, 150)


def fg(s, code):
    return f'\x1b[{code}m{s}\x1b[39m'


def w255(s):
    return fg(s, '97')


def w200(s):
    return rgb(s, 200)


def red(s):
    return fg(s, 31)


def green(s):
    # return f'[green]{s}[/green]'
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


color_regex = re.compile("(\x1B\\[)[0-?]*[ -/]*[@-~]")


def strip_color(s):
    """Strip color from string."""
    rv = color_regex.sub("", s)
    return rv


def len_color(s):
    """Compute how long the color escape sequences in the string are."""
    return len(s) - len(strip_color(s))


def ljust_with_color(s: str, width):
    """ljust string that might contain color."""
    return s.ljust(width + len_color(s))
