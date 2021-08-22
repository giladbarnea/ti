from test.testutils import assert_raises
from timefred.dikt import DiktField


# TODO:
#  - arbitrary attrs

class DictSubclass(dict):
    pass


class ConvertsEverythingToDiktField(DictSubclass):
    # TODO: implement
    #  date: str = 'DD/MM/YY' # becomes DiktField
    ...


def test__get__setitem_in_instance():
    """Tests that dikt['foo'] has the computed value after getting attribute"""

    class HasDiktField(DictSubclass):
        foo = DiktField(default_factory=lambda x: x + 1)
        bar = DiktField(int)
        baz = DiktField()

        def __init__(self, foo) -> None:
            super().__init__()
            self.foo = foo

    # TODO: turn everything to Field on __setattr__
    has_diktfield = HasDiktField(5)
    assert has_diktfield.foo == 6
    assert has_diktfield['foo'] == 6
    assert has_diktfield.foo == 6

    has_diktfield.foo = 10
    assert has_diktfield.foo == 11
    assert has_diktfield['foo'] == 11

    has_diktfield.bar = '5'
    assert has_diktfield.bar == 5
    assert has_diktfield['bar'] == 5


def test__get__getitem_in_instance():
    class HasDiktField(DictSubclass):
        foo = DiktField()

    has_diktfield = HasDiktField()
    has_diktfield['foo'] = 'bar'
    assert has_diktfield.foo == 'bar'
    assert has_diktfield['foo'] == 'bar'

    class DoesntSupportGetitem:
        foo = DiktField()

    doesnt_support_getitem = DoesntSupportGetitem()
    doesnt_support_getitem.foo = 'bar'
    with assert_raises(TypeError, "'DoesntSupportGetitem' object does not support item assignment"):
        # The line that fails is `instance[field.name] = rv` in cache()
        doesnt_support_getitem.foo == 'bar'


def test__annotated_with_default():
    class TimeFormats(DictSubclass):
        date = DiktField(default='DD/MM/YY')
        short_date = DiktField(default='DD/MM')
        date_time = DiktField(default='DD/MM/YY HH:mm:ss')
        time = DiktField(default='HH:mm:ss')

    time_formats = TimeFormats()
    assert time_formats.date == 'DD/MM/YY'
    assert time_formats.short_date == 'DD/MM'
    assert time_formats.date_time == 'DD/MM/YY HH:mm:ss'
    assert time_formats.time == 'HH:mm:ss'

def test__set__type_coersion():
    class Person(DictSubclass):
        age: int = DiktField()

    person = Person()
    person.age = '5'
    assert type(person.age) is int
    assert type(person['age']) is int