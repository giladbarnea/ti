from timefred.dikt import Dikt, DefaultDikt, Field, DiktField
from test.testutils import assert_raises
from pytest import mark



def test__annotated_with_default():
    class Config(Dikt):
        class TimeCfg(Dikt):
            class TimeFormats(Dikt):
                date: str = 'DD/MM/YY'
                short_date: str = 'DD/MM'
                date_time: str = 'DD/MM/YY HH:mm:ss'
                time: str = 'HH:mm:ss'

            formats: TimeFormats

        hobbies: list
        time: TimeCfg
        dev: Dikt = {"debugger": None, "traceback": None}

    config = Config()
    assert isinstance(config.dev, Dikt)
    assert config.dev.debugger is None
    assert config.dev.traceback is None


def test__doctest():
    import doctest
    from timefred import dikt
    failed, attempted = doctest.testmod(dikt)
    assert not failed


class Foo(Dikt):
    class Bar(Dikt):
        baz: int = 5

    bar: Bar


def test__init_mismatches_annotation_but_buildable():
    foo = Foo(bar={'baz': 6})
    bar = getattr(foo, 'bar')
    assert isinstance(bar, Foo.Bar)
    baz = getattr(bar, 'baz')
    assert baz == 6


def test__init_mismatches_annotation_but_not_buildable():
    foo = Foo(bar={'baz': 'NOT A NUMBER'})
    bar = foo.bar
    assert isinstance(bar, Foo.Bar)
    with assert_raises(ValueError):
        baz = bar.baz


@mark.skip('dict() is not implemented yet')
def test__dict():
    foo = Foo(bar={'baz': 6})
    assert isinstance(foo.bar, Foo.Bar)
    assert foo.bar.baz == 6
    foo_dict = foo.dict()
    assert isinstance(foo_dict, dict)
    assert foo_dict['bar'] == {'baz': 6}


def test__get__attr_item_symmetry():
    foo = Foo(bar={'baz': 6})
    bar = getattr(foo, 'bar')
    assert isinstance(bar, Foo.Bar)
    assert isinstance(foo['bar'], Foo.Bar)
    assert foo.bar == foo['bar'] == bar
    baz = getattr(bar, 'baz')
    assert baz == 6
    assert foo['bar']['baz'] == 6
    assert foo.bar['baz'] == 6
    assert foo['bar'].baz == 6
    assert foo.bar.baz == 6


def test__set__attr_item_symmetry__setattr():
    foo = Foo()
    bar = Foo.Bar()
    baz = 6
    bar.baz = baz
    assert bar.baz == 6
    assert bar['baz'] == 6
    foo.bar = bar
    assert foo.bar == bar
    assert foo.bar == foo['bar'] == bar
    assert foo['bar']['baz'] == 6
    assert foo.bar['baz'] == 6
    assert foo['bar'].baz == 6
    assert foo.bar.baz == 6

    foo.bar.baz = 5
    assert baz == 6 # primitive
    assert bar.baz == 5



def test__set__attr_item_symmetry__setitem():
    foo = Foo()
    bar = Foo.Bar()
    baz = 6
    bar['baz'] = baz
    assert bar.baz == 6
    assert bar['baz'] == 6
    foo['bar'] = bar
    assert foo.bar == bar
    assert foo.bar == foo['bar'] == bar
    assert foo['bar']['baz'] == 6
    assert foo.bar['baz'] == 6
    assert foo['bar'].baz == 6
    assert foo.bar.baz == 6

    foo['bar']['baz'] = 5
    assert baz == 6 # primitive
    assert bar.baz == 5

    foo['bar'].baz = 4
    assert baz == 6
    assert bar.baz == 4
    assert bar['baz'] == 4

    foo.bar['baz'] = 3
    assert baz == 6
    assert bar.baz == 3
    assert bar['baz'] == 3


def test__set__type_coersion():
    class Person(Dikt):
        age: int

    person = Person()
    person.age = '5'
    assert type(person.age) is int
    assert type(person['age']) is int


######################
# *** DefaultDikt
######################

def test__defaultdikt__annotated():
    class Config(DefaultDikt):
        class TimeCfg(DefaultDikt):
            class TimeFormats(Dikt):
                date: str = 'DD/MM/YY'
                short_date: str = 'DD/MM'
                date_time: str = 'DD/MM/YY HH:mm:ss'
                time: str = 'HH:mm:ss'

            formats: TimeFormats

        hobbies: list
        time: TimeCfg
        dev: Dikt = {"debugger": None, "traceback": None}

    config = Config()
    assert config.hobbies == []
    assert isinstance(config.time, Config.TimeCfg)
    assert isinstance(config.time, DefaultDikt)
    assert isinstance(config.time.formats, Config.TimeCfg.TimeFormats)
    assert isinstance(config.time.formats, Dikt)
    assert config.time.formats.date == 'DD/MM/YY'
    assert config.time.formats.short_date == 'DD/MM'
    assert config.time.formats.date_time == 'DD/MM/YY HH:mm:ss'
    assert config.time.formats.time == 'HH:mm:ss'



@mark.skip('Fails because iterable typings isnt working, e.g return lambda *args: origin(map(type_args[0], *args))')
def test__annotated_as_generic():
    class GenericDikt(DefaultDikt):
        foo: DefaultDikt[{'bar': list}]
    dikt = GenericDikt()
    assert isinstance(dikt.foo, DefaultDikt)
    assert dikt.foo.bar == []



######################
# *** Field
######################

def test_dikt_with_field():
    print('\n\n\n')
    class BaseDiktMock(dict):
        pass

    class BaseDiktMockWithField(BaseDiktMock):
        foo = DiktField(default_factory=lambda x: x + 1)

        def __init__(self, foo) -> None:
            super().__init__()
            self.foo = foo

        # def __getattribute__(self, name):
        #     """Makes d.foo return d['foo']"""
        #     try:
        #         item = super().__getitem__(name)
        #         return item
        #     except KeyError as e:
        #         attr = super().__getattribute__(name)
        #         return attr

        # def __setattr__(self, name: str, value) -> None:
        #     """Makes d.foo = 'bar' also set d['foo']"""
        #     super().__setattr__(name, value)
        #     self[name] = value

    # TODO: turn everything to Field on __setattr__
    dikt_with_field = BaseDiktMockWithField(5)
    assert dikt_with_field.foo == 6
    assert dikt_with_field['foo'] == 6
    assert dikt_with_field.foo == 6
    dikt_with_field.foo = 10
    assert dikt_with_field.foo == 11
    assert dikt_with_field['foo'] == 11

######################
# *** Edge Cases
######################

# TODO:
#  returns None explicitly and not UNSET

######################
# *** Native dict methods
######################

# TODO:
#  setdefault()

def test__contains__():
    dikt = Dikt()
    dikt.foo = 'bar'
    assert 'foo' in dikt
    assert hasattr(dikt, 'foo')

def test__update():
    dikt = Dikt()
    dikt.update(foo='bar')
    assert dikt.foo == 'bar'
    assert dikt['foo'] == 'bar'
    assert 'foo' in dikt
    assert hasattr(dikt, 'foo')