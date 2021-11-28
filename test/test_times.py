import sys
from collections.abc import Iterable
from copy import copy
from typing import NoReturn, Union

from arrow.locales import EnglishLocale
from icecream import ic

from test import TEST_START_ARROW
from timefred.config import config
from timefred.log import log
from timefred.time import XArrow
from random import randint, random
from arrow import Arrow
from pdbpp import break_on_exc
from itertools import product
import pytest

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
        except AttributeError as e:
            raise AssertionError(f'{obj1!r}.{attribute} not equal to {obj2!r}.{attribute} because AttributeError: {e}') from None


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

class TestXArrow:
    def test_from_day(self):
        days = ['sunday', 'monday', 'tuesday',
                'wednesday', 'thursday', 'friday', 'saturday']
        
        for num, day in enumerate(days, start=1):
            for char_index in range(2, len(day) + 1):
                arrow_from_day = XArrow.from_day(day[:char_index])
                assert arrow_from_day.strftime('%A').lower() == day
        
    
    class TestDehumanize:
        # @break_on_exc
        @pytest.mark.slow
        def test_dehumanize_vanilla(self):
            """Make sure we don't break vanilla Arrow.dehumanize() functionality"""
            log.title('TestXArrow.TestDehumanize.test_dehumanize_vanilla')
            now = XArrow.now()
            now_dehumanized = XArrow.dehumanize("now")
            assert_arrows_soft_eq(now_dehumanized, now)
            assert_arrows_soft_eq(XArrow.dehumanize("just now"), now)
            # * 1 unit
            for unit, expression in EnglishLocale.timeframes.items():
                # "hour": "an hour", "days": "{0} days"
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
                                    "{0}, {1}, {2}",       "{0}, {1} and {2}", "{0}, {1} {2}",
                                    "{0} {1} {2}",         "{0} {1}, {2}",     "{0} {1} and {2}",
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
            assert_equal_attrs(now, yesterday, TIME_UNITS - {'day'})
            assert_arrows_soft_eq(now.shift(days=-1), yesterday)
    
            tomorrow = XArrow.dehumanize('tomorrow')
            assert_equal_attrs(now, tomorrow, TIME_UNITS - {'day'})
            assert_arrows_soft_eq(now.shift(days=+1), tomorrow)
            
        def test_dehumanize_instance(self):
            now = XArrow.now()
            yesterday = XArrow.dehumanize('yesterday')
            tomorrow = XArrow.dehumanize('tomorrow')
            _1_days_ago = now.dehumanize('1 days ago')
            assert_arrows_soft_eq(_1_days_ago, yesterday)
            
            _1_day_ago = now.dehumanize('1 day ago')
            assert_arrows_soft_eq(_1_day_ago, yesterday)
    
            in_1_days = now.dehumanize('in 1 days')
            assert_arrows_soft_eq(in_1_days, tomorrow)
    
            in_1_day = now.dehumanize('in 1 day')
            assert_arrows_soft_eq(in_1_day, tomorrow)
    
            now.dehumanize('1d ago')
            
        def test_dehumanize_advanced(self): # can decide not to support if too difficult
            XArrow.dehumanize('1 days from now')
            XArrow.dehumanize('1 days from today')
    
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
    
    
    def test_from_absolute(self):
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
            from_absolute: XArrow = XArrow.from_absolute(now.format(fmt))
            assert_arrows_soft_eq(from_absolute, now)
    
    