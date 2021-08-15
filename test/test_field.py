import inspect
import re

from test.testutils import assert_raises
from timefred.dikt import Field
from timefred.dikt.dikt import UNSET


def test__get__():
    class HasField:
        foo = Field()

    has_field = HasField()
    with assert_raises(AttributeError, re.compile(r"HasField object has no attribute '_foo', and HasField\.foo Field's `default` and `default_factory` are both unset")):
        getattr(has_field, 'foo')

    class HasFieldWithDefault:
        foo = Field(default='bar')

    has_field_w_default = HasFieldWithDefault()
    assert has_field_w_default.foo == 'bar'

    class HasFieldWithDefaultFactory:
        foo = Field(default_factory=list)

    has_field_w_default_factory = HasFieldWithDefaultFactory()
    assert has_field_w_default_factory.foo == list()

    class HasFieldWithDefaultValueAndFactory:
        foo = Field(default='hi', default_factory=list)

    has_field_w_default_val_and_factory = HasFieldWithDefaultValueAndFactory()
    assert has_field_w_default_val_and_factory.foo == ['h', 'i']


def test__cached_value__():
    class HasFieldWithDefault:
        foo = Field(default='bar')

    has_field_w_default = HasFieldWithDefault()
    foo_field = inspect.getattr_static(has_field_w_default, 'foo')
    assert foo_field.__cached_value__ is UNSET
    assert has_field_w_default.foo == 'bar'
    assert foo_field.__cached_value__ == 'bar'

    class HasFieldWithDefaultFactory:
        foo = Field(default_factory=list)

    has_field_w_default_factory = HasFieldWithDefaultFactory()
    foo_field = inspect.getattr_static(has_field_w_default_factory, 'foo')
    assert foo_field.__cached_value__ is UNSET
    assert has_field_w_default_factory.foo == list()
    assert foo_field.__cached_value__ == list()


    class HasFieldWithDefaultValueAndFactory:
        foo = Field(default=1, default_factory=lambda x:x+1)

    has_field_w_default_val_and_factory = HasFieldWithDefaultValueAndFactory()
    foo_field = inspect.getattr_static(has_field_w_default_val_and_factory, 'foo')
    assert foo_field.__cached_value__ is UNSET
    assert has_field_w_default_val_and_factory.foo == 2
    assert has_field_w_default_val_and_factory.foo == 2
    assert foo_field.__cached_value__ == 2


def test__set__():
    class HasField:
        foo = Field()

        def __init__(self, foo) -> None:
            self.foo = foo

    has_field = HasField("bar")
    assert has_field.foo == "bar"

    class HasFieldWithDefaultFactory:
        foo = Field(default_factory=str)
        increases = Field(default_factory=lambda x:x+1)

        def __init__(self, foo) -> None:
            self.foo = foo

    has_field_w_default_factory = HasFieldWithDefaultFactory(42)
    foo_field = inspect.getattr_static(has_field_w_default_factory, 'foo')
    assert foo_field.__cached_value__ is UNSET  # __cached_value__ is only set in __get__, after applying default_factory
    assert has_field_w_default_factory.foo == '42'
    assert foo_field.__cached_value__ == '42'

    has_field_w_default_factory.foo = 1337
    assert foo_field.__cached_value__ is UNSET  # __cached_value__ = UNSET in __set__
    assert has_field_w_default_factory.foo == '1337'
    assert foo_field.__cached_value__ == '1337'

    increases_field = inspect.getattr_static(has_field_w_default_factory, 'increases')
    assert increases_field.__cached_value__ is UNSET
    has_field_w_default_factory.increases = 1
    assert increases_field.__cached_value__ is UNSET
    assert has_field_w_default_factory.increases == 2
    assert increases_field.__cached_value__ == 2
    # does not increase if has __cached_value__:
    assert has_field_w_default_factory.increases == 2
    assert increases_field.__cached_value__ == 2

    has_field_w_default_factory.increases = 10
    assert increases_field.__cached_value__ is UNSET
    assert has_field_w_default_factory.increases == 11
    assert increases_field.__cached_value__ == 11
    # does not increase if has __cached_value__:
    assert has_field_w_default_factory.increases == 11
    assert increases_field.__cached_value__ == 11


def test__delete__():
    class HasField:
        foo = Field()

        def __init__(self, foo) -> None:
            self.foo = foo

    has_field = HasField("bar")
    assert has_field.foo == "bar"

    del has_field.foo
    with assert_raises(AttributeError, re.compile(r"HasField object has no attribute '_foo', and HasField\.foo Field's `default` and `default_factory` are both unset")):
        getattr(has_field, 'foo')

    foo_field = inspect.getattr_static(has_field, 'foo')
    assert foo_field.__cached_value__ is UNSET
