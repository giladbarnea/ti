from collections import namedtuple
from datetime import timedelta

from timefred.time.timeutils import secs2human
from timefred.time.xarrow import XArrow


class Timespan(namedtuple('Timespan', 'start end')):
    start: XArrow
    end: XArrow

    def __radd__(self, other) -> int:
        self_seconds = self.seconds()
        try:
            return self_seconds + int(other.timedelta().total_seconds())
        except AttributeError: # other is int
            return self_seconds + other

    def timedelta(self) -> timedelta:
        return self.end - self.start

    def seconds(self) -> int:
        return int(self.timedelta().total_seconds())

    def human_duration(self) -> str:
        return secs2human(self.seconds())