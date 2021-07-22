import re
from typing import Optional

from arrow import Arrow

from ti.times import formatted2arrow
from ti.xarrow import XArrow

NOTE_TIME_RE = re.compile(r'(.+) \(([\d/: ]+)\)', re.IGNORECASE)

class Note:
    time: Optional[XArrow]
    content: str

    def __init__(self, note: str):
        match = NOTE_TIME_RE.fullmatch(note)
        if match:
            match_groups = match.groups()
            self.content = match_groups[0]
            self._time = match_groups[1]
        else:
            self.content = note
            self._time = None

    @property
    def time(self) -> XArrow:
        if self._time and not isinstance(self._time, Arrow):
            self._time = formatted2arrow(self._time)
        return self._time
