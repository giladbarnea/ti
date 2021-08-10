from contextlib import contextmanager
import re
from typing import Union, Type


@contextmanager
def assert_raises(exc: Type[BaseException] = BaseException, match_exc_arg: Union[str, re.Match] = None):
    try:
        yield
    except exc as e:
        if match_exc_arg:
            escaped = re.escape(match_exc_arg)
            if not any(re.search(escaped, arg) for arg in map(str, e.args)):
                raise
        assert True
    except BaseException as e:
        raise

@contextmanager
def assert_doesnt_raise(exc: Type[BaseException] = BaseException, match_exc_arg: Union[str, re.Match] = None):
    try:
        yield
    except exc as e:
        if not match_exc_arg or any(re.search(re.escape(match_exc_arg), arg) for arg in map(str, e.args)):
            raise
        assert True
    except BaseException as e:
        pass
