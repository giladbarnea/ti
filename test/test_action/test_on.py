import os

# from test.test_times import _arrow_assert_soft_eq
from test.testutils import assert_raises
from timefred.color import Colored
from timefred.space import DefaultDictSpace
from timefred.store import Day, Entry, Activity
from timefred.time import XArrow
from timefred.store import store
from timefred.log import log
# import debug

test_start = XArrow.now()

class TestEmptySheet:
    def test_on_got_to_office_08_20(self):
        work = DefaultDictSpace(Day)
        '''{ "02/11/21" : Day }'''
        assert isinstance(work, DefaultDictSpace)
        assert isinstance(work, dict)
        assert not work
        assert len(work) == 0
        
        entry = Entry(start="02:20")
        assert entry
        assert entry.start
        assert isinstance(entry.start, XArrow)
        assert entry.start == XArrow.from_formatted("02:20")
        
        name = "Got to office"
        activity = Activity(name=name)
        assert not activity # because list
        assert len(activity) == 0
        assert isinstance(activity.name, Colored)
        assert activity.name == name
        
        activity.append(entry)
        assert activity
        assert len(activity) == 1
        assert activity[0] == entry
        
        day = work[entry.start.DDMMYY]
        assert isinstance(day, Day)
        day[name] = activity
        assert day[name] == activity, f"{day[str(activity.name)] = }, {activity = }"
        assert work
        assert len(work) == 1
    
class TestSheetWithContent:
    class TestOngoingActivity:
        
        @staticmethod
        def default_work() -> DefaultDictSpace:
            sheet = {
                test_start.DDMMYY: {
                    "Got to office": [{"start": "02:20"}]
                    }
                }
            work = DefaultDictSpace(Day, **sheet)
            return work
            

        class TestOnDeviceValidation08_30:
            def test_sanity(self, work=None):
                log.title(f"test_sanity({work = })")
                if not work:
                    work = TestSheetWithContent.TestOngoingActivity.default_work()
                    
                log.debug('work (DefaultDictSpace)')
                assert isinstance(work, DefaultDictSpace)
                assert work
                assert len(work) == 1
                assert test_start.DDMMYY in work
    
                log.debug('day (Day)')
                day: Day = work[test_start.DDMMYY]
                assert isinstance(day, Day)
                assert day
                assert len(day) == 1
                assert "Got to office" in day
    
                log.debug('got_to_office_activity: Activity = day["Got to office"]')
                got_to_office_activity: Activity = day["Got to office"]
                assert isinstance(got_to_office_activity, Activity)
                assert got_to_office_activity
                assert len(got_to_office_activity) == 1
                #assert repr(got_to_office_activity) == "Activity(name='Got to office') [{'start': '02:20'}]"
                assert isinstance(got_to_office_activity.name, Colored)
                got_to_office_activity_is_ongoing = got_to_office_activity.ongoing()
                assert got_to_office_activity_is_ongoing is True
                assert got_to_office_activity.name == "Got to office"
    
                log.debug('device_validation_activity: Activity = day["On Device Validation"]')
                name = "On Device Validation"
                device_validation_activity: Activity = day[name]
                assert isinstance(device_validation_activity, Activity)
                assert device_validation_activity.name == "On Device Validation"
                assert not device_validation_activity
                assert len(device_validation_activity) == 0
                #assert repr(device_validation_activity) == f"Activity(name='{name}') []"
                assert isinstance(device_validation_activity.name, Colored)
                device_validation_activity_is_ongoing = device_validation_activity.ongoing()
                assert device_validation_activity_is_ongoing is False
                
                log.debug('ongoing_activity: Activity = day.ongoing_activity()')
                ongoing_activity: Activity = day.ongoing_activity()
                log.debug('assert ongoing_activity')
                assert ongoing_activity
                log.debug('assert isinstance(ongoing_activity, Activity)')
                assert isinstance(ongoing_activity, Activity)
                log.debug('assert ongoing_activity.name == "Got to office"')
                assert ongoing_activity.name == "Got to office"
                assert isinstance(ongoing_activity.name, Colored)
                assert len(ongoing_activity) == 1
                assert ongoing_activity != device_validation_activity

                assert device_validation_activity.name == "On Device Validation"
                assert ongoing_activity.name == "Got to office"
                
                log.debug('got_to_office_end_time: XArrow = ongoing_activity.stop()')
                got_to_office_end_time: XArrow = ongoing_activity.stop()
                log.debug('assert isinstance(got_to_office_end_time, XArrow)')
                assert isinstance(got_to_office_end_time, XArrow)
                # _arrow_assert_soft_eq(got_to_office_end_time, now)
                log.debug('assert not ongoing_activity.ongoing()')
                assert not ongoing_activity.ongoing()
                with assert_raises(Exception):
                    ongoing_activity.stop()
                    
                log.debug('assert day.ongoing_activity() is None')
                assert day.ongoing_activity() is None
                assert work[test_start.DDMMYY].ongoing_activity() is None

            def test_load_store(self, work=None):
                log.title(f"test_load_store({work = })")
                os.environ['TF_SHEET'] = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
                from timefred.config import config
                config.sheet.path = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
                store.filename = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
                
                if not work:
                    log.debug('work = TestSheetWithContent.TestOngoingActivity.default_work()')
                    work = TestSheetWithContent.TestOngoingActivity.default_work()
                store.dump(work)
                
                log.debug('work = store.load()')
                work = store.load()
                self.test_sanity(work=work)
