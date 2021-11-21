import sys
from copy import copy
from typing import NoReturn

from timefred.time import isoweekday, XArrow
from timefred.config import config
test_start = XArrow.now()

def _arrow_assert_soft_eq(arrw1: XArrow, arrw2: XArrow) -> NoReturn:
    """Regular Arrow __eq__ compares microseconds as well"""
    _arrow_assert_same_day(arrw1, arrw2)
    _arrow_assert_same_time(arrw1, arrw2)


def _arrow_assert_same_day(arrw1: XArrow, arrw2: XArrow) -> NoReturn:
    assert arrw1.year == arrw2.year
    assert arrw1.month == arrw2.month
    assert arrw1.day == arrw2.day


def _arrow_assert_same_time(arrw1: XArrow, arrw2: XArrow) -> NoReturn:
    assert arrw1.hour == arrw2.hour
    assert arrw1.minute == arrw2.minute
    assert arrw1.second == arrw2.second


# def test__human2arrow():
#     now = arrow.now(TZINFO)
#
#     # 'now', 'today', 'yesterday'
#     arrw = human2arrow("now")
#     _arrow_assert_soft_eq(arrw, now)
#     _arrow_assert_same_day(human2arrow('today'), now)
#     _arrow_assert_same_day(human2arrow(), now)
#     _arrow_assert_same_day(human2arrow('yesterday'), now.shift(days=-1))
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
#                 _arrow_assert_soft_eq(arrw, now2)
#
#     # '1h 3m ago'
#     _arrow_assert_soft_eq(human2arrow('1h 3m ago'), now.shift(hours=-1, minutes=-3))
#     _arrow_assert_soft_eq(human2arrow('1h 3m 8s ago'), now.shift(hours=-1, minutes=-3, seconds=-8))
#     _arrow_assert_soft_eq(human2arrow('1h 3 minutes'), now.shift(hours=-1, minutes=-3))
#     _arrow_assert_soft_eq(human2arrow('1hr 8 secs'), now.shift(hours=-1, seconds=-8))
#
#     # '09:45'
#     for _ in range(20):
#         h = str(randint(0, 23))
#         m = str(randint(0, 59))
#
#         _arrow_assert_same_day(human2arrow(f'{h}:{m}'), now)
#         _arrow_assert_same_day(human2arrow(f'{h}'), now)
#         _arrow_assert_same_day(human2arrow(f'{h.ljust(1, "0")}:{m}'), now)
#         _arrow_assert_same_day(human2arrow(f'{h.ljust(1, "0")}'), now)
#
#     # 'Wednesday'
#     wednesday = human2arrow('Wednesday')
#     _arrow_assert_same_time(wednesday, now)
#
#     # 'Wednesday 09:45'
#     wednesday_morning = human2arrow('Wed 09:45')
#     today_morning = now.replace(hour=9, minute=45)
#     _arrow_assert_same_day(wednesday_morning, wednesday)
#     assert wednesday_morning.hour == 9
#     assert wednesday_morning.minute == 45
#     _arrow_assert_same_time(wednesday_morning, today_morning)

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
#     _arrow_assert_same_day(arrw, now)
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
