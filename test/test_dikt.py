print()
import os

os.environ['TF_FEATURE_DIKT_ANNOTATE_GETATTR'] = 'true'
from timefred.dikt import Dikt
from test.util import assert_raises
from pytest import mark


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


@mark.skip('Field(default_factory=list) is not implemented yet')
def test__annotated_no_default():
    config = Config()
    assert config.hobbies == []
    assert isinstance(config.time, Config.TimeCfg)
    assert isinstance(config.time, Dikt)
    assert isinstance(config.time.formats, Config.TimeCfg.TimeFormats)
    assert isinstance(config.time.formats, Dikt)
    assert config.time.formats.date == 'DD/MM/YY'
    assert config.time.formats.short_date == 'DD/MM'
    assert config.time.formats.date_time == 'DD/MM/YY HH:mm:ss'
    assert config.time.formats.time == 'HH:mm:ss'


def test__annotated_with_default():
    config = Config()
    assert isinstance(config.dev, Dikt)
    assert config.dev.debugger is None
    assert config.dev.traceback is None


def test__doctest():
    import doctest
    from timefred import dikt
    failed, attempted = doctest.testmod(dikt)
    assert not failed


class GenericDikt(Dikt):
    foo: Dikt[{'bar': list}]


@mark.skip('Field(default_factory=list) is not implemented yet')
def test__annotated_as_generic():
    dikt = GenericDikt()
    assert isinstance(dikt.foo, Dikt)
    assert dikt.foo.bar == []


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
