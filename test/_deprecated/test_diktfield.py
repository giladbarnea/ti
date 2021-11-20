from test.testutils import assert_raises
from timefred.dikt import DiktField


# TODO:
#  - arbitrary attrs
from timefred.dikt.dikt import UNSET


class DictSubclass(dict):
    pass



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
    assert time_formats.date == time_formats['date'] == 'DD/MM/YY'
    assert time_formats.short_date == time_formats['short_date'] == 'DD/MM'
    assert time_formats.date_time == time_formats['date_time'] == 'DD/MM/YY HH:mm:ss'
    assert time_formats.time == time_formats['time'] == 'HH:mm:ss'


def test__get__type_coersion():
    class Person(DictSubclass):
        age: int = DiktField()
        name = DiktField(default_factory=str)

    person = Person()
    person.age = '5'
    assert type(person.age) is int
    assert type(person['age']) is int
    assert person.age == person['age'] == 5
    person.name = 5
    assert type(person.name) is str
    assert type(person['name']) is str
    assert person.name == person['name'] == '5'


def test__default_and_default_factory():
    class HasBothDefaultAndDefaultFactory(DictSubclass):
        foo = DiktField(default=1, default_factory=lambda x: x + 1)
        bar: str = DiktField(default=10)

    has_both_default_and_default_factory = HasBothDefaultAndDefaultFactory()
    assert (has_both_default_and_default_factory.foo == 2)
    assert (has_both_default_and_default_factory.bar == '10')

# TODO - note:
# class BuildsDiktFieldFromClassVar(DictSubclass):
#     has_value_and_annotation: str = "gilad"
#     only_annotation: str
#     has_value_no_annotation = "old style"
#     def __init__(self) -> None:
#         dir_self = set(dir(self))
#         attrs = dir_self - DONT_ANNOTATE  # {'has_value_no_annotation', 'has_value_and_annotation', 'foo'}
#         annots = self.__annotations__     # {'has_value_and_annotation': <class 'str'>, 'only_annotation': <class 'str'>}
#     def foo(self): ...

# TODO - account for:
#  1. superclass has classvar, not inheriting class
#  2. classvar is already a Field
class BuildsDiktFieldFromClassVar(DictSubclass):
    # TODO: implement
    #  date: str = 'DD/MM/YY' # becomes DiktField
    ...


class BuildsDiktFieldFromAnnotation(DictSubclass):
    # TODO: implement
    #  date: str # becomes DiktField
    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError as e:
            annotation = super().__getattribute__('__annotations__')[item]
            field = DiktField(default_factory=annotation, name=item)
            # cls = super().__getattribute__('__class__')
            # setattr(cls, name, field)
            setattr(type(self), item, field)
            return setattr(self, field.private_name, UNSET)
            return getattr(self, item)
            return field

def test__build_diktfield_from_annotation():
    class Person(BuildsDiktFieldFromAnnotation):
        name: str
    
    person = Person()
    assert isinstance(person.name, str)
