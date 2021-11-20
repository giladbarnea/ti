import re

NONWORD_RE = re.compile(r'[\W_]')
COLOR_RE = re.compile(r'(\x1b\[(?:\d;?)*m)')
WHITESPACE_RE = re.compile(r'\s+')

def normalize_str(s):
    # if hasattr(s, '__normalized__'):
    #     return s
    # normalized = NONWORD_RE.sub('', s.lower().strip())
    # normalized.__normalized__ = True
    # return normalized
    return NONWORD_RE.sub('', s.lower().strip())

def decolor(s):
    return COLOR_RE.sub('', s)


def shorten(s, limit=80) -> str:
    if not s:
        return s
    if limit < 4:
        import logging
        logging.warning(f"shorten({shorten(repr(s), limit=20)}) was called with limit = %d, can handle limit >= 4", limit)
        return s
    if not isinstance(s, str):
        s = str(s)
    length = len(s)
    if length <= limit:
        return s
    half_the_limit = limit // 2
    if '\033[' in s:
        no_color = decolor(s)
        real_length = len(no_color)
        if real_length <= limit:
            return s
        color_matches: list[re.Match] = list(COLOR_RE.finditer(s))
        if len(color_matches) == 2:
            color_a, color_b = color_matches
            if color_a.start() == 0 and color_b.end() == length:
                # Colors surround string from both ends
                return f'{color_a.group()}{shorten(no_color, limit)}{color_b.group()}'
        return shorten(no_color, limit)
        # escape_seq_start_rindex = s.rindex('\033')
        # left_cutoff = max(escape_seq_start_index + 4, half_the_limit)
        # right_cutoff = min((real_length - escape_seq_start_rindex) + 4, half_the_limit)
        # print(f'{limit = } | {length = } | {real_length = } | {left_cutoff = } | {right_cutoff = } | {half_the_limit = } | {escape_seq_start_index = } | {escape_seq_start_rindex = }')
    left_cutoff = max(half_the_limit - 3, 1)
    right_cutoff = max(half_the_limit - 4, 1)
    # print(f'{limit = } | {length = } | {left_cutoff = } | {right_cutoff = } | {half_the_limit = }')
    free_chars = limit - left_cutoff - right_cutoff
    assert free_chars > 0, f'{free_chars = } not > 0'
    beginning = s[:left_cutoff]
    end = s[-right_cutoff:]
    if free_chars >= 7:
        separator = ' [...] '
    elif free_chars >= 5:
        separator = '[...]'
    elif free_chars >= 4:
        separator = ' .. '
    else:
        separator = '.' * free_chars
    assert len(separator) <= free_chars, f'{len(separator) = } ! <= {free_chars = }'
    return WHITESPACE_RE.sub(' ', f'{beginning}{separator}{end}')
