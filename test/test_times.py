import sys
from collections.abc import Iterable
from copy import copy
# from pdbpp import break_on_exc
from itertools import product, permutations
from random import randint, random
from typing import NoReturn, Union

import pytest
from arrow import Arrow
from arrow.locales import EnglishLocale
from icecream import ic

from test import TEST_START_ARROW
from timefred.config import config
from timefred.log import log
from timefred.time import XArrow
from timefred.time.timeutils import secs2human, arrows2rel_time

ic.configureOutput(prefix='')

FORMATS = config.time.formats
TIME_UNITS = {'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second'}


def assert_equal_attrs(obj1, obj2, attr: Union[str, Iterable[str]], *attrs) -> NoReturn:
    __tracebackhide__ = True
    if not isinstance(attr, str):
        if attrs:
            raise ValueError('If attr is iterable, attrs must be empty')
        attributes = attr
    else:
        attributes = (attr, *attrs)
    for attribute in attributes:
        try:
            assert getattr(obj1, attribute) == getattr(obj2, attribute)
        except AttributeError as attr_err:
            raise AssertionError(f'{obj1!r}.{attribute} not equal to {obj2!r}.{attribute} because AttributeError: {attr_err}') from None


def assert_arrows_soft_eq(arrow1: Arrow, arrow2: Arrow, *, compare_second=True) -> NoReturn:
    """Compares year, month, day, hour, minute, second.
    No microseconds (unlike vanilla Arrow.__eq__)"""
    __tracebackhide__ = True
    assert_arrows_same_day(arrow1, arrow2)
    assert_arrows_same_time(arrow1, arrow2, compare_second=compare_second)


def assert_arrows_same_day(arrow1: Arrow, arrow2: Arrow) -> NoReturn:
    """Compares year, month, day"""
    __tracebackhide__ = True
    assert_equal_attrs(arrow1, arrow2, 'year', 'month', 'day')


def assert_arrows_same_time(arrow1: Arrow, arrow2: Arrow, *, compare_second=True) -> NoReturn:
    """Compares hour, minute, second"""
    __tracebackhide__ = True
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
#         now2 = now.shift(**{TIME_UNITS_FIRST_DIGIT_TO_PLURAL[unit[0]]: -1})
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

def test_isoweekday():
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
        for char_index in range(2, len(day) + 1):
            assert isoweekday(day[:char_index]) == num
    
    config.time.first_day_of_week = 'monday'
    [sys.modules.pop(k) for k in list(sys.modules.keys()) if k.startswith('timefred.time')]
    from timefred.time import isoweekday
    # noinspection PyUnresolvedReferences
    assert sys.modules['timefred.time.timeutils'].NUM2DAY[0][1] == 'monday'
    days = ['monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday']
    for num, day in enumerate(days, start=1):
        assert isoweekday(day) == num
        for char_index in range(2, len(day) + 1):
            assert isoweekday(day[:char_index]) == num
    
    config.time.first_day_of_week = orig_first_day_of_week
    [sys.modules.pop(k) for k in list(sys.modules.keys()) if k.startswith('timefred.time')]
    # noinspection PyUnresolvedReferences
    from timefred.time import isoweekday


def test_arrows2rel_time():
    present = XArrow.now()
    past = present.shift(weeks=-3, days=-3)
    assert arrows2rel_time(present, past) == '3 weeks & 3 days ago'
    
    present = XArrow.from_absolute('21/12/21')
    past = XArrow.from_absolute('01/12/21')
    secs = int((present - past).total_seconds())
    assert 20 * 24 * 3600 <= secs <= 21 * 24 * 3600
    ret = arrows2rel_time(present, past)
    assert ret == '2 weeks & 6 days ago'


class Test_secs2human:
    def test_1_unit(self):
        assert secs2human(0) == ''
        assert secs2human(1) == '1 second'
        assert secs2human(2) == '2 seconds'
        assert secs2human(60) == '1 minute'
        assert secs2human(120) == '2 minutes'
        assert secs2human(60 * 60) == '1 hour'
        assert secs2human(60 * 60 * 2) == '2 hours'
        assert secs2human(60 * 60 * 24) == '1 day'
        assert secs2human(60 * 60 * 24 * 2) == '2 days'
        assert secs2human(60 * 60 * 24 * 7) == '1 week'
        assert secs2human(60 * 60 * 24 * 7 * 2) == '2 weeks'
        assert secs2human(60 * 60 * 24 * 7 * 52) == '1 year'
        assert secs2human(60 * 60 * 24 * 7 * 52 * 2) == '2 years'
    
    def test_2_units(self):
        assert secs2human(61) == '1 minute & 1 second'
        assert secs2human(121) == '2 minutes & 1 second'
        assert secs2human(122) == '2 minutes & 2 seconds'
        assert secs2human(60 * 60 * 24 + 1) == '1 day & 1 second'
    
    def test_3_units(self):
        assert secs2human(60 * 60 + 61) == '1 hour, 1 minute & 1 second'
        assert secs2human(60 * 60 + 62) == '1 hour, 1 minute & 2 seconds'
        assert secs2human(60 * 61 + 62) == '1 hour, 2 minutes & 2 seconds'
        assert secs2human(2 * 60 * 61 + 62) == '2 hours, 3 minutes & 2 seconds'
    
    def test_4_units(self):
        minute = 60
        hour = minute * 60
        day = hour * 24
        week = day * 7
        assert secs2human(week + day + hour + minute) == '1 week, 1 day, 1 hour & 1 minute'
        assert secs2human(week + day + hour + 2 * minute) == '1 week, 1 day, 1 hour & 2 minutes'
        assert secs2human(week + day + 2 * hour + 2 * minute) == '1 week, 1 day, 2 hours & 2 minutes'
        assert secs2human(week + 2 * day + 2 * hour + 2 * minute) == '1 week, 2 days, 2 hours & 2 minutes'
        assert secs2human(2 * week + 2 * day + 2 * hour + 2 * minute) == '2 weeks, 2 days, 2 hours & 2 minutes'


class TestXArrow:
    def test_from_day(self):
        days = ['sunday', 'monday', 'tuesday',
                'wednesday', 'thursday', 'friday', 'saturday']
        
        for num, day in enumerate(days, start=1):
            for char_index in range(2, len(day) + 1):
                arrow_from_day = XArrow.from_day(day[:char_index])
                assert arrow_from_day.strftime('%A').lower() == day
    
    def test_from_formatted(self):
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
            formatted = TEST_START_ARROW.format(fmt)
            from_formatted: XArrow = XArrow.from_formatted(formatted)
            assert_equal_attrs(from_formatted, TEST_START_ARROW, *expected_attrs)
            for not_included_attr in TIME_UNITS - set(expected_attrs):
                assert getattr(from_formatted, not_included_attr) == 0 if not_included_attr in {'hour', 'minute', 'second'} else 1
    
    def test_sub(self):
        minute = 60
        hour = minute * 60
        day = hour * 24
        week = day * 7
        present = XArrow.now()
        past = present.shift(weeks=-3, days=-3)
        td = present - past
        assert td.days == 3 * 7 + 3
        secs = int(td.total_seconds())
        assert secs == 3 * week + 3 * day
    
    class Test_dehumanize:
        # @break_on_exc
        @pytest.mark.slow
        def test_dehumanize_vanilla(self):
            """Make sure we don't break vanilla Arrow.dehumanize() functionality"""
            log.title('TestXArrow.Test_dehumanize.test_dehumanize_vanilla')
            now = XArrow.now()
            now_dehumanized = XArrow.dehumanize("now")
            assert_arrows_soft_eq(now_dehumanized, now)
            assert_arrows_soft_eq(XArrow.dehumanize("just now"), now)
            # * 1 unit
            # "hour": "an hour", "days": "{0} days"
            for unit, expression in EnglishLocale.timeframes.items():
                for relative_fmt in ("{0} ago", "in {0}"):
                    if 'now' in expression:
                        continue
                    if '{0}' in expression:
                        shift = randint(2, 4)
                        hardcoded_number = expression.format(shift)  # 3 seconds
                        human_expression = relative_fmt.format(hardcoded_number)  # 3 seconds ago / in 3 seconds
                    else:
                        shift = 1
                        human_expression = relative_fmt.format(expression)  # a second ago / in a second
                    dehumanized_static = XArrow.dehumanize(human_expression)
                    
                    if 'ago' in relative_fmt:
                        shift *= -1
                    shift_kwargs = {unit.removesuffix('s') + 's': shift}
                    now = XArrow.now()
                    now_shifted = now.shift(**shift_kwargs)
                    try:
                        assert_arrows_soft_eq(dehumanized_static, now_shifted)
                    except AssertionError:
                        dehumanized_static = XArrow.dehumanize(human_expression)
                        now = XArrow.now()
                        now_shifted = now.shift(**shift_kwargs)
                        assert_arrows_soft_eq(dehumanized_static, now_shifted)
                    
                    dehumanized_instance = now.dehumanize(human_expression)
                    assert_arrows_soft_eq(dehumanized_instance, now_shifted)
            
            # * 2 units
            for time_unit_1 in TIME_UNITS:
                for time_unit_2 in TIME_UNITS:
                    if time_unit_1 == time_unit_2:
                        continue
                    if random() < 0.5:
                        continue
                    shift_1 = randint(2, 4)
                    shift_2 = randint(2, 4)
                    singular_time_unit_1 = (f"a" if time_unit_1 != "hour" else "an") + f" {time_unit_1}"
                    singular_time_unit_2 = (f"a" if time_unit_2 != "hour" else "an") + f" {time_unit_2}"
                    plural_time_unit_1 = f"{shift_1} {time_unit_1}s"
                    plural_time_unit_2 = f"{shift_2} {time_unit_2}s"
                    expressions = {}
                    for fmt in ["{0} and {1}", "{0}, {1}", "{0} {1}"]:
                        expressions[fmt.format(plural_time_unit_1, plural_time_unit_2) + " ago"] = (True, True)
                        expressions["in " + fmt.format(plural_time_unit_1, plural_time_unit_2)] = (True, True)
                        expressions[fmt.format(plural_time_unit_1, singular_time_unit_2) + " ago"] = (True, False)
                        expressions["in " + fmt.format(plural_time_unit_1, singular_time_unit_2)] = (True, False)
                        expressions[fmt.format(singular_time_unit_1, plural_time_unit_2) + " ago"] = (False, True)
                        expressions["in " + fmt.format(singular_time_unit_1, plural_time_unit_2)] = (False, True)
                        expressions[fmt.format(singular_time_unit_1, singular_time_unit_2) + " ago"] = (False, False)
                        expressions["in " + fmt.format(singular_time_unit_1, singular_time_unit_2)] = (False, False)
                    
                    for human_expression, quantity_tuple in expressions.items():
                        shift_kwargs = {}
                        sign = 1 if human_expression.startswith("in ") else -1
                        if quantity_tuple[0]:
                            shift_kwargs[time_unit_1 + 's'] = shift_1 * sign
                        else:
                            shift_kwargs[time_unit_1 + 's'] = 1 * sign
                        
                        if quantity_tuple[1]:
                            shift_kwargs[time_unit_2 + 's'] = shift_2 * sign
                        else:
                            shift_kwargs[time_unit_2 + 's'] = 1 * sign
                        
                        now = XArrow.now()
                        dehumanized_instance_vanilla = Arrow.now().dehumanize(human_expression)
                        dehumanized_instance_vanilla.microsecond = 0
                        dehumanized_static = XArrow.dehumanize(human_expression)
                        
                        now_shifted = now.shift(**shift_kwargs)
                        dehumanized_instance = now.dehumanize(human_expression)
                        
                        try:
                            assert_arrows_soft_eq(dehumanized_instance, now_shifted)
                            assert_arrows_soft_eq(dehumanized_static, now_shifted)
                            assert_arrows_soft_eq(dehumanized_instance, dehumanized_instance_vanilla)
                            assert_arrows_soft_eq(dehumanized_static, dehumanized_instance_vanilla)
                        except AssertionError:
                            now = XArrow.now()
                            dehumanized_instance = now.dehumanize(human_expression)
                            now_shifted = now.shift(**shift_kwargs)
                            assert_arrows_soft_eq(dehumanized_instance, now_shifted)
                            dehumanized_static = XArrow.dehumanize(human_expression)
                            assert_arrows_soft_eq(dehumanized_static, now_shifted)
                            dehumanized_instance_vanilla = Arrow.now().dehumanize(human_expression)
                            assert_arrows_soft_eq(dehumanized_instance, dehumanized_instance_vanilla)
                            assert_arrows_soft_eq(dehumanized_static, dehumanized_instance_vanilla)
                    
                    # * 3 units
                    for time_unit_3 in TIME_UNITS:
                        if time_unit_3 == time_unit_1 or time_unit_3 == time_unit_2:
                            continue
                        if random() < 0.75:
                            continue
                        shift_3 = randint(2, 4)
                        singular_time_unit_3 = (f"a" if time_unit_3 != "hour" else "an") + f" {time_unit_3}"
                        plural_time_unit_3 = f"{shift_3} {time_unit_3}s"
                        expressions = {}
                        for fmt in ["{0} and {1} and {2}", "{0} and {1}, {2}", "{0} and {1} {2}",
                                    "{0}, {1}, {2}", "{0}, {1} and {2}", "{0}, {1} {2}",
                                    "{0} {1} {2}", "{0} {1}, {2}", "{0} {1} and {2}",
                                    ]:
                            for q1, q2, q3 in product(["plural", "singular"], ["plural", "singular"], ["plural", "singular"]):
                                past_human_expression = eval(f"fmt.format({q1}_time_unit_1, {q2}_time_unit_2, {q3}_time_unit_3) + ' ago'")
                                future_human_expression = eval(f"'in ' + fmt.format({q1}_time_unit_1, {q2}_time_unit_2, {q3}_time_unit_3)")
                                quantity_tuple = (q1 == "plural", q2 == "plural", q3 == "plural")
                                expressions[past_human_expression] = quantity_tuple
                                expressions[future_human_expression] = quantity_tuple
                        for human_expression, quantity_tuple in expressions.items():
                            shift_kwargs = {}
                            sign = 1 if human_expression.startswith("in ") else -1
                            if quantity_tuple[0]:
                                shift_kwargs[time_unit_1 + 's'] = shift_1 * sign
                            else:
                                shift_kwargs[time_unit_1 + 's'] = 1 * sign
                            
                            if quantity_tuple[1]:
                                shift_kwargs[time_unit_2 + 's'] = shift_2 * sign
                            else:
                                shift_kwargs[time_unit_2 + 's'] = 1 * sign
                            
                            if quantity_tuple[2]:
                                shift_kwargs[time_unit_3 + 's'] = shift_3 * sign
                            else:
                                shift_kwargs[time_unit_3 + 's'] = 1 * sign
                            
                            now = XArrow.now()
                            dehumanized_instance_vanilla = Arrow.now().dehumanize(human_expression)
                            dehumanized_static = XArrow.dehumanize(human_expression)
                            
                            now_shifted = now.shift(**shift_kwargs)
                            dehumanized_instance = now.dehumanize(human_expression)
                            
                            try:
                                assert_arrows_soft_eq(dehumanized_instance, now_shifted)
                                assert_arrows_soft_eq(dehumanized_static, now_shifted)
                                assert_arrows_soft_eq(dehumanized_instance, dehumanized_instance_vanilla)
                                assert_arrows_soft_eq(dehumanized_static, dehumanized_instance_vanilla)
                            except AssertionError:
                                now = XArrow.now()
                                dehumanized_instance = now.dehumanize(human_expression)
                                now_shifted = now.shift(**shift_kwargs)
                                assert_arrows_soft_eq(dehumanized_instance, now_shifted)
                                dehumanized_static = XArrow.dehumanize(human_expression)
                                assert_arrows_soft_eq(dehumanized_static, now_shifted)
                                dehumanized_instance_vanilla = Arrow.now().dehumanize(human_expression)
                                assert_arrows_soft_eq(dehumanized_instance, dehumanized_instance_vanilla)
                                assert_arrows_soft_eq(dehumanized_static, dehumanized_instance_vanilla)
        
        def test_dehumanize_static(self):
            now_dehumanized = XArrow.dehumanize("now")
            now = XArrow.now()
            assert_arrows_soft_eq(now_dehumanized, now)
            
            today = XArrow.dehumanize('today')
            assert_arrows_soft_eq(today, now)
            
            yesterday = XArrow.dehumanize('yesterday')
            now_shift_yesterday = now.shift(days=-1)
            assert_arrows_soft_eq(now_shift_yesterday, yesterday)
            
            tomorrow = XArrow.dehumanize('tomorrow')
            now_shift_tomorrow = now.shift(days=+1)
            assert_arrows_soft_eq(now_shift_tomorrow, tomorrow)
        
        def test_dehumanize_instance(self):
            now = XArrow.now()
            now_dehumanized = now.dehumanize("now")
            assert_arrows_soft_eq(now_dehumanized, now)
            
            today = now.dehumanize('today')
            assert_arrows_soft_eq(today, now)
            assert_arrows_soft_eq(today, now_dehumanized)
            
            # * Past
            # 1 day ago
            yesterday = now.dehumanize('yesterday')
            assert_arrows_soft_eq(now.shift(days=-1), yesterday)
            
            a_day_ago = now.dehumanize('a day ago')
            assert_arrows_soft_eq(a_day_ago, yesterday)
            
            _1_day_ago = now.dehumanize('1 day ago')
            assert_arrows_soft_eq(_1_day_ago, yesterday)
            
            _1d_ago = now.dehumanize('1d ago')
            assert_arrows_soft_eq(_1d_ago, yesterday)
            
            _1_days_ago = now.dehumanize('1 days ago')
            assert_arrows_soft_eq(_1_days_ago, yesterday)
            
            _1_d_ago = now.dehumanize('1 d ago')
            assert_arrows_soft_eq(_1_d_ago, yesterday)
            
            a_day = now.dehumanize('a day')
            assert_arrows_soft_eq(a_day, yesterday)
            
            _1_day = now.dehumanize('1 day')
            assert_arrows_soft_eq(_1_day, yesterday)
            
            _1d = now.dehumanize('1d')
            assert_arrows_soft_eq(_1d, yesterday)
            
            _1_d = now.dehumanize('1 d')
            assert_arrows_soft_eq(_1_d, yesterday)
            
            _1_days = now.dehumanize('1 days')
            assert_arrows_soft_eq(_1_days, yesterday)
            
            # 5 days ago
            five_days_ago = now.shift(days=-5)
            
            _5_day_ago = now.dehumanize('5 day ago')
            assert_arrows_soft_eq(_5_day_ago, five_days_ago)
            
            _5d_ago = now.dehumanize('5d ago')
            assert_arrows_soft_eq(_5d_ago, five_days_ago)
            
            _5_days_ago = now.dehumanize('5 days ago')
            assert_arrows_soft_eq(_5_days_ago, five_days_ago)
            
            _5_d_ago = now.dehumanize('5 d ago')
            assert_arrows_soft_eq(_5_d_ago, five_days_ago)
            
            _5_day = now.dehumanize('5 day')
            assert_arrows_soft_eq(_5_day, five_days_ago)
            
            _5d = now.dehumanize('5d')
            assert_arrows_soft_eq(_5d, five_days_ago)
            
            _5_d = now.dehumanize('5 d')
            assert_arrows_soft_eq(_5_d, five_days_ago)
            
            _5_days = now.dehumanize('5 days')
            assert_arrows_soft_eq(_5_days, five_days_ago)
            
            # months
            _5_months = now.dehumanize('5 months')
            assert_arrows_soft_eq(_5_months, now.shift(months=-5))
            
            _5_month = now.dehumanize('5 month')
            assert_arrows_soft_eq(_5_month, now.shift(months=-5))
            
            # Complex
            _5h_32m_1s_ago = now.dehumanize('5h 32m 1s ago')
            assert_arrows_soft_eq(_5h_32m_1s_ago, now.shift(hours=-5, minutes=-32, seconds=-1))
            
            _5_minutes_5_months = now.dehumanize('5 minutes 5 months')
            assert_arrows_soft_eq(_5_minutes_5_months, now.shift(minutes=-5, months=-5))
            
            _5m_5_months = now.dehumanize('5m 5 months')
            assert_arrows_soft_eq(_5m_5_months, now.shift(minutes=-5, months=-5))
            
            _5m_5M = now.dehumanize('5m 5M')
            assert_arrows_soft_eq(_5m_5M, now.shift(minutes=-5, months=-5))
            
            _5m_5M_7w = now.dehumanize('5m 5M 7w')
            now_shift_5_minutes_5_months_7_weeks_ago = now.shift(minutes=-5, months=-5, weeks=-7)
            assert_arrows_soft_eq(_5m_5M_7w, now_shift_5_minutes_5_months_7_weeks_ago)
            
            for perm in permutations(['5m', '5M', '7w'], 3):
                complex = now.dehumanize(' '.join(perm))
                assert_arrows_soft_eq(complex, now_shift_5_minutes_5_months_7_weeks_ago)
            
            # * Future
            in_1_days = now.dehumanize('in 1 days')
            tomorrow = now.dehumanize('tomorrow')
            assert_arrows_soft_eq(in_1_days, tomorrow)
            assert_arrows_soft_eq(now.shift(days=+1), tomorrow)
            assert_arrows_soft_eq(now.shift(days=+1), in_1_days)
            
            in_1_day = now.dehumanize('in 1 day')
            assert_arrows_soft_eq(in_1_day, tomorrow)
            
            in_5_days = now.dehumanize('in 5 days')
            assert_arrows_soft_eq(now.shift(days=+5), in_5_days)
            
            in_5_day = now.dehumanize('in 5 day')
            assert_arrows_soft_eq(in_5_day, now.shift(days=+5))
            
            now_shift_in_5_minutes_5_months_7_weeks = now.shift(minutes=+5, months=+5, weeks=+7)
            for perm in permutations(['5m', '5M', '7w'], 3):
                complex = now.dehumanize('in ' + ' '.join(perm))
                assert_arrows_soft_eq(complex, now_shift_in_5_minutes_5_months_7_weeks)
        
        @pytest.mark.skip
        def test_dehumanize_advanced(self):  # can decide not to support if too difficult
            XArrow.dehumanize('1 days from now')
            XArrow.dehumanize('1 days from today')
    
    class Test_from_human:
        def test_from_human_static(self):
            now = XArrow.from_human('now')
            today = XArrow.from_human('today')
            assert now == today == XArrow.now()
            yesterday = XArrow.from_human('yesterday')
            assert yesterday == now.shift(days=-1)
            assert yesterday.day == now.day - 1
            eight_days_ago = XArrow.from_human('8 days ago')
            assert eight_days_ago == now.shift(days=-8)
            assert eight_days_ago.day == now.day - 8
            dec_first_21 = XArrow.from_human('01/12/21')
            assert dec_first_21.year == 2021
            assert dec_first_21.month == 12
            assert dec_first_21.day == 1
            thursday = XArrow.from_human('thursday')
            assert thursday.strftime('%A') == 'Thursday'
    
    class Test_from_absolute:
        def test_from_absolute_time(self):
            from datetime import time
            abs_time = time(hour=11, minute=0, second=0)
            from_absolute = XArrow.from_absolute(abs_time)
            assert from_absolute.hour == 11
            assert from_absolute.minute == 0
            assert from_absolute.second == 0

            abs_time = time(hour=11, minute=23, second=0)
            from_absolute = XArrow.from_absolute(abs_time)
            assert from_absolute.hour == 11
            assert from_absolute.minute == 23
            assert from_absolute.second == 0

            abs_time = time(hour=11, minute=23, second=45)
            from_absolute = XArrow.from_absolute(abs_time)
            assert from_absolute.hour == 11
            assert from_absolute.minute == 23
            assert from_absolute.second == 45

            abs_time = time(hour=11, minute=0, second=45)
            from_absolute = XArrow.from_absolute(abs_time)
            assert from_absolute.hour == 11
            assert from_absolute.minute == 0
            assert from_absolute.second == 45

            abs_time = time(hour=0, minute=0, second=45)
            from_absolute = XArrow.from_absolute(abs_time)
            assert from_absolute.hour == 0
            assert from_absolute.minute == 0
            assert from_absolute.second == 45

            abs_time = time(hour=0, minute=23, second=45)
            from_absolute = XArrow.from_absolute(abs_time)
            assert from_absolute.hour == 0
            assert from_absolute.minute == 23
            assert from_absolute.second == 45
        def test_from_absolute_now(self):
            now = XArrow.now().replace(second=0)
            from_absolute_now = XArrow.from_absolute(now)
            assert_arrows_soft_eq(from_absolute_now, now)
            assert from_absolute_now is now
            
            for fmt in [  # FORMATS.date,
                # FORMATS.short_date:       ['month', 'day'],
                FORMATS.time,
                FORMATS.short_time,
                # FORMATS.datetime:         ['year', 'month', 'day', 'hour', 'minute', 'second'],
                # FORMATS.shorter_datetime: ['year', 'month', 'day', 'hour', 'minute'],
                # FORMATS.short_datetime:   ['month', 'day', 'hour', 'minute'],
                ]:
                formatted = now.format(fmt)
                from_absolute_formatted: XArrow = XArrow.from_absolute(formatted)
                assert_arrows_soft_eq(from_absolute_formatted, now)
        
        def test_from_absolute_HHmmss(self):
            HHmmss = "02:00:00"
            from_absolute = XArrow.from_absolute(HHmmss)
            assert from_absolute.hour == 2
            assert from_absolute.minute == 0
            assert from_absolute.second == 0
            
            HHmmss = "02:53:49"
            from_absolute = XArrow.from_absolute(HHmmss)
            assert from_absolute.hour == 2
            assert from_absolute.minute == 53
            assert from_absolute.second == 49
        
        def test_from_absolute_HHmm(self):
            HHmm = "02:00"
            from_absolute = XArrow.from_absolute(HHmm)
            assert from_absolute.hour == 2
            assert from_absolute.minute == 0
            assert from_absolute.second == 0
        
        def test_from_absolute_DDMMYY(self):
            DDMMYY = "13/12/21"
            from_absolute = XArrow.from_absolute(DDMMYY)
            assert from_absolute.day == 13
            assert from_absolute.month == 12
            assert from_absolute.year == 2021

        def test_from_absolute_DDMMYYHHmmss(self):
            datetime = "13/12/21 11:23:45"
            from_absolute = XArrow.from_absolute(datetime)
            assert from_absolute.day == 13
            assert from_absolute.month == 12
            assert from_absolute.year == 2021
            assert from_absolute.hour == 11
            assert from_absolute.minute == 23
            assert from_absolute.second == 45

            datetime = "13/12 11:23:45"
            from_absolute = XArrow.from_absolute(datetime)
            assert from_absolute.day == 13
            assert from_absolute.month == 12
            assert from_absolute.hour == 11
            assert from_absolute.minute == 23
            assert from_absolute.second == 45

            datetime = "13/12/21 11:23"
            from_absolute = XArrow.from_absolute(datetime)
            assert from_absolute.day == 13
            assert from_absolute.month == 12
            assert from_absolute.year == 2021
            assert from_absolute.hour == 11
            assert from_absolute.minute == 23
            assert from_absolute.second == 0

            datetime = "13/12 11:23"
            from_absolute = XArrow.from_absolute(datetime)
            assert from_absolute.day == 13
            assert from_absolute.month == 12
            assert from_absolute.hour == 11
            assert from_absolute.minute == 23
            assert from_absolute.second == 00