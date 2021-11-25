import sys
from copy import copy
from typing import NoReturn

from test import TEST_START_ARROW
from timefred.config import config
from timefred.log import log
from timefred.time import XArrow

FORMATS = config.time.formats


def assert_equal_attrs(obj1, obj2, attr: str, *attrs) -> NoReturn:
    for attribute in [attr, *attrs]:
        try:
            assert getattr(obj1, attribute) == getattr(obj2, attribute)
        except AttributeError as e:
            raise AssertionError(f'{obj1!r}.{attribute} not equal to {obj2!r}.{attribute} because AttributeError: {e}') from e


def assert_arrows_soft_eq(arrow1: XArrow, arrow2: XArrow, *, compare_second=True) -> NoReturn:
    """Compares year, month, day, hour, minute, second.
    No microseconds (unlike vanilla Arrow.__eq__)"""
    assert_arrows_same_day(arrow1, arrow2)
    assert_arrows_same_time(arrow1, arrow2, compare_second=compare_second)


def assert_arrows_same_day(arrow1: XArrow, arrow2: XArrow) -> NoReturn:
    """Compares year, month, day"""
    assert_equal_attrs(arrow1, arrow2, 'year', 'month', 'day')


def assert_arrows_same_time(arrow1: XArrow, arrow2: XArrow, *, compare_second=True) -> NoReturn:
    """Compares hour, minute, second"""
    if compare_second:
        attrs = ['hour', 'minute', 'second']
    else:
        attrs = ['hour', 'minute']
    assert_equal_attrs(arrow1, arrow2, *attrs)


# def test__human2arrow():
#     now = arrow.now(TZINFO)
#
#     # 'now', 'today', 'yesterday'
#     arrw = human2arrow("now")
#     assert_arrows_soft_eq(arrw, now)
#     assert_arrows_same_day(human2arrow('today'), now)
#     assert_arrows_same_day(human2arrow(), now)
#     assert_arrows_same_day(human2arrow('yesterday'), now.shift(days=-1))
#
#     # '1m ago'
#     for unit in ('s', 'sec', 'secs', 'second', 'seconds',
#                  'm', 'min', 'mins', 'minute', 'minutes',
#                  'h', 'hr', 'hrs', 'hour', 'hours',
#                  'd', 'day', 'days'):
#         # sometimes fails because a second passes
#         now2 = now.shift(**{ABBREVS[unit[0]]: -1})
#         for foo in (unit, f' {unit}'):  # "s", " s"
#
#             for bar in (foo, f'{foo} ago'):  # "s",  "s ago"
#                 arrw = human2arrow('1' + bar)
#                 assert arrw is not None
#                 assert_arrows_soft_eq(arrw, now2)
#
#     # '1h 3m ago'
#     assert_arrows_soft_eq(human2arrow('1h 3m ago'), now.shift(hours=-1, minutes=-3))
#     assert_arrows_soft_eq(human2arrow('1h 3m 8s ago'), now.shift(hours=-1, minutes=-3, seconds=-8))
#     assert_arrows_soft_eq(human2arrow('1h 3 minutes'), now.shift(hours=-1, minutes=-3))
#     assert_arrows_soft_eq(human2arrow('1hr 8 secs'), now.shift(hours=-1, seconds=-8))
#
#     # '09:45'
#     for _ in range(20):
#         h = str(randint(0, 23))
#         m = str(randint(0, 59))
#
#         assert_arrows_same_day(human2arrow(f'{h}:{m}'), now)
#         assert_arrows_same_day(human2arrow(f'{h}'), now)
#         assert_arrows_same_day(human2arrow(f'{h.ljust(1, "0")}:{m}'), now)
#         assert_arrows_same_day(human2arrow(f'{h.ljust(1, "0")}'), now)
#
#     # 'Wednesday'
#     wednesday = human2arrow('Wednesday')
#     assert_arrows_same_time(wednesday, now)
#
#     # 'Wednesday 09:45'
#     wednesday_morning = human2arrow('Wed 09:45')
#     today_morning = now.replace(hour=9, minute=45)
#     assert_arrows_same_day(wednesday_morning, wednesday)
#     assert wednesday_morning.hour == 9
#     assert wednesday_morning.minute == 45
#     assert_arrows_same_time(wednesday_morning, today_morning)

def test__isoweekday():
    orig_first_day_of_week = copy(config.time.first_day_of_week)
    config.time.first_day_of_week = 'sunday'
    [sys.modules.pop(k) for k in list(sys.modules.keys()) if k.startswith('timefred.time')]
    from timefred.time import isoweekday
    # noinspection PyUnresolvedReferences
    assert sys.modules['timefred.time.timeutils'].NUM2DAY[0][1] == 'sunday'
    days = ['sunday', 'monday', 'tuesday',
            'wednesday', 'thursday', 'friday', 'saturday']
    
    for num, day in enumerate(days, start=1):
        assert isoweekday(day) == num
        for i, char in enumerate(day[2:], start=2):
            assert isoweekday(day[:i]) == num
    
    config.time.first_day_of_week = 'monday'
    [sys.modules.pop(k) for k in list(sys.modules.keys()) if k.startswith('timefred.time')]
    from timefred.time import isoweekday
    # noinspection PyUnresolvedReferences
    assert sys.modules['timefred.time.timeutils'].NUM2DAY[0][1] == 'monday'
    days = ['monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday']
    for num, day in enumerate(days, start=1):
        assert isoweekday(day) == num
        for i, char in enumerate(day[2:], start=2):
            assert isoweekday(day[:i]) == num
    
    config.time.first_day_of_week = orig_first_day_of_week
    [sys.modules.pop(k) for k in list(sys.modules.keys()) if k.startswith('timefred.time')]
    # noinspection PyUnresolvedReferences
    from timefred.time import isoweekday


def test__XArrow_from_day():
    sunday = XArrow._from_day('sun')
    saturday = XArrow._from_day('sat')
    assert sunday.day - saturday.day == 1
    friday = XArrow._from_day('friday')
    assert sunday.day - friday.day == 2
    assert isinstance(sunday, XArrow)
    assert isinstance(saturday, XArrow)


# def test__formatted2arrow():
#     arrw = formatted2arrow('19/04/21 10:13:11')
#     assert arrw.year == 2021
#     assert arrw.month == 4
#     assert arrw.day == 19
#     assert arrw.hour == 10
#     assert arrw.minute == 13
#     assert arrw.second == 11
#
#     arrw = formatted2arrow('19/04/21')
#     assert arrw.year == 2021
#     assert arrw.month == 4
#     assert arrw.day == 19
#
#     arrw = formatted2arrow('10:13:11')
#     now = arrow.now()
#     assert_arrows_same_day(arrw, now)
#
#     assert arrw.hour == 10
#     assert arrw.minute == 13
#     assert arrw.second == 11


def test__XArrow_from_human():
    assert XArrow.from_human() is not None
    now = XArrow.now()
    assert now.format(fmt="HH") == str(now.hour).rjust(2, '0')
    # assert human2formatted('07:39', fmt="HH") == '07'
    # assert human2formatted('07:39', fmt="mm") == '39'


def test__XArrow_from_formatted():
    test_start_from_formatted = XArrow.from_formatted(TEST_START_ARROW)
    assert_arrows_soft_eq(test_start_from_formatted, TEST_START_ARROW)
    assert test_start_from_formatted is TEST_START_ARROW
    
    for fmt, expected_attrs in {
        FORMATS.date:             ['year', 'month', 'day'],
        FORMATS.short_date:       ['month', 'day'],
        FORMATS.time:             ['hour', 'minute', 'second'],
        FORMATS.short_time:       ['hour', 'minute'],
        FORMATS.datetime:         ['year', 'month', 'day', 'hour', 'minute', 'second'],
        FORMATS.shorter_datetime: ['year', 'month', 'day', 'hour', 'minute'],
        FORMATS.short_datetime:   ['month', 'day', 'hour', 'minute'],
        }.items():
        from_formatted: XArrow = XArrow.from_formatted(TEST_START_ARROW.format(fmt))
        assert_equal_attrs(from_formatted, TEST_START_ARROW, *expected_attrs)
        for not_included_attr in {'year', 'month', 'day', 'hour', 'minute', 'second'} - set(expected_attrs):
            assert getattr(from_formatted, not_included_attr) == 0 if not_included_attr in {'hour', 'minute', 'second'} else 1


def test__XArrow_from_absolute():
    now = XArrow.now()
    now_from_absolute = XArrow.from_absolute(now)
    assert_arrows_soft_eq(now_from_absolute, now)
    assert now_from_absolute is now
    
    for fmt in [  # FORMATS.date,
        # FORMATS.short_date:       ['month', 'day'],
        FORMATS.time,
        FORMATS.short_time,
        # FORMATS.datetime:         ['year', 'month', 'day', 'hour', 'minute', 'second'],
        # FORMATS.shorter_datetime: ['year', 'month', 'day', 'hour', 'minute'],
        # FORMATS.short_datetime:   ['month', 'day', 'hour', 'minute'],
        ]:
        log.debug(f"{fmt = !r}")
        from_absolute: XArrow = XArrow.from_absolute(now.format(fmt))
        log.debug(f" {from_absolute = !r}")
        assert_arrows_soft_eq(from_absolute, now)
        # for not_included_attr in {'year', 'month', 'day', 'hour', 'minute', 'second'} - set(expected_attrs):
        #     assert getattr(from_absolute, not_included_attr) == 0 if not_included_attr in {'hour', 'minute', 'second'} else 1