class TIError(Exception):
    """Errors raised by TI."""


class EmptySheet(TIError):
    """Sheet has no data."""


class NoActivities(TIError):
    """No activities at specified time"""

    def __init__(self, time, *args: object) -> None:
        super().__init__(*(f"No activities at {time}", *args))


class AlreadyOn(TIError):
    """Already working on that task."""


class NoEditor(TIError):
    """No $EDITOR set."""


class InvalidYAML(TIError):
    """No $EDITOR set."""


class NoTask(TIError):
    """Not working on a task yet."""


class BadTime(TIError):
    """Time string can't be parsed."""


class BadArguments(TIError):
    """The command line arguments passed are not valid."""