import os
import re
from contextlib import contextmanager
from typing import Union, Type
from pathlib import Path

from timefred.config import config
from timefred.store import Work, Day, store
from timefred.time import XArrow
from time import time_ns


@contextmanager
def assert_raises(exc: Type[Exception], match: Union[str, re.Pattern] = None):
    __tracebackhide__ = True
    exc_name = exc.__qualname__
    try:
        yield
    except exc as e:
        if not match:
            return True
        if isinstance(match, re.Pattern):
            escaped = match
        else:
            escaped = re.escape(match)
        for arg in map(str, e.args):
            if re.search(escaped, arg):
                return True
        error = '\n'.join([
            f'{exc_name} was raised but did not match expected exception args.',
            f'Expected: {match!r}',
            f'Actual: {"; ".join(map(str, e.args))!r}',
            ])
        raise AssertionError(error) from e
    except Exception as e:
        raise AssertionError(f"{e.__class__.__qualname__} was raised, NOT {exc_name}") from e
    else:
        raise AssertionError(f"{exc_name} was not raised")


@contextmanager
def assert_doesnt_raise(exc: Type[BaseException] = BaseException, match_exc_arg: Union[str, re.Pattern] = None):
    try:
        yield
    except exc as e:
        if not match_exc_arg or any(re.search(re.escape(match_exc_arg), arg) for arg in map(str, e.args)):
            raise
        assert True
    except BaseException as e:
        pass

def default_work(day: XArrow = None) -> Work:
    """
    Returns Work of one day with a single activity, "Got to office": [{"start": "02:20"}]
    """
    if not day:
        day = XArrow.now()
    sheet = {
        day.DDMMYY: {
            "Got to office": [{"start": "02:20:00"}],
            # "Integration": [{"start": "02:20:00", "end": "02:30:00"}]
            }
        }
    work = Work(Day, **sheet)
    return work


@contextmanager
def temp_sheet(path, rm=True, backup=True):
    old_path = config.sheet.path
    if 'TIMEFRED_SHEET' in os.environ and os.environ['TIMEFRED_SHEET'] != old_path != store.path:
        raise ValueError(f"Original sheet path config mismatch: "
                         f"{os.environ['TIMEFRED_SHEET'] = !r}, {config.sheet.path = !r}, {store.path = !r}")
    
    if backup:
        now_ns = int(time_ns())
        store._backup(f'_{now_ns}')
    os.environ['TIMEFRED_SHEET'] = path
    path = Path(path)
    config.sheet.path = path
    store.path = path
    store._store = None # forces StoreProxy to re init a Store
    
    try:
        yield
    except:
        rm = False
    finally:
        old_path = Path(old_path)
        os.environ['TIMEFRED_SHEET'] = str(old_path)
        config.sheet.path = old_path
        store.path = old_path
        if rm:
            path.unlink(True)
            if backup:
                backup_path = (config.cache.path / old_path.name).with_name(old_path.stem + f'_{now_ns}.backup')
                backup_path.unlink(True)
            