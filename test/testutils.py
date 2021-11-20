from contextlib import contextmanager
import re
from typing import Union, Type


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

