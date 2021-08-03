from timefred.dikt import Dikt


class Config(Dikt):
    class TimeCfg(Dikt):
        class TimeFormats(Dikt):
            date: str = 'DD/MM/YY'
            short_date: str = 'DD/MM'
            date_time: str = 'DD/MM/YY HH:mm:ss'
            time: str = 'HH:mm:ss'

        formats: TimeFormats

    time: TimeCfg
    dev: Dikt = {"debugger": None, "traceback": None}


def test__annotated_no_default():
    config = Config()
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
    dev = config.dev
    actual = isinstance(dev, Dikt)
    assert actual

def test__doctest():
    import doctest
    from timefred import dikt
    failed, attempted = doctest.testmod(dikt)
    assert not failed