import os
from timefred.store import store
from test import TEST_START_ARROW
from test.test_times import assert_arrows_soft_eq
from test.testutils import assert_raises, default_work, temp_sheet
from timefred.color import Colored
from timefred.store import Day, Activity, Work, Entry
from timefred.time import XArrow
from timefred.log import log

class TestEmptySheet:
    def test_on_got_to_office_08_20(self):
        work = Work()
        '''{ "02/11/21" : Day }'''
        assert isinstance(work, Work)
        assert isinstance(work, dict)
        assert not work
        assert len(work) == 0
        
        entry = Entry(start="02:20")
        assert entry
        assert entry.start
        assert isinstance(entry.start, XArrow)
        absolute = XArrow.from_absolute("02:20")
        entry_start = entry.start
        assert_arrows_soft_eq(entry_start, absolute)
        
        name = "Got to office"
        activity = Activity(name=name)
        assert not activity  # because list
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
    class TestWithOngoingActivity:
        class TestOnDeviceValidation08_30:
            def test_sanity(self, work=None):
                log.title(f"test_sanity({work = })")
                if not work:
                    work = default_work(TEST_START_ARROW)
                
                log.debug('work (Work)')
                assert isinstance(work, Work)
                assert work
                assert len(work) == 1
                assert TEST_START_ARROW.DDMMYY in work
                log.debug('Work["30/12/99"] -> Day')
                day: Day = work[TEST_START_ARROW.DDMMYY]
                assert isinstance(day, Day)
                assert day
                assert len(day) == 1
                assert "Got to office" in day
                
                log.debug('Day["Got to office"] -> Activity (ongoing)')
                got_to_office_activity: Activity = day["Got to office"]
                assert isinstance(got_to_office_activity, Activity)
                assert got_to_office_activity
                assert len(got_to_office_activity) == 1
                assert isinstance(got_to_office_activity.name, Colored)
                got_to_office_activity_is_ongoing = got_to_office_activity.ongoing()
                assert got_to_office_activity_is_ongoing is True
                assert got_to_office_activity.name == "Got to office"
                
                log.debug('Day["On Device Validation"] -> Activity (not ongoing)')
                device_validation_activity: Activity = day["On Device Validation"]
                
                assert got_to_office_activity.name == "Got to office"
                assert isinstance(device_validation_activity, Activity)
                assert device_validation_activity.name == "On Device Validation"
                assert not device_validation_activity
                assert len(device_validation_activity) == 0
                assert isinstance(device_validation_activity.name, Colored)
                device_validation_activity_is_ongoing = device_validation_activity.ongoing()
                assert device_validation_activity_is_ongoing is False
                
                log.debug('Work.ongoing_activity() -> Activity')
                ongoing_activity: Activity = work.ongoing_activity()
                assert ongoing_activity
                assert isinstance(ongoing_activity, Activity)
                assert ongoing_activity.name == "Got to office"
                assert isinstance(ongoing_activity.name, Colored)
                assert len(ongoing_activity) == 1
                assert ongoing_activity.ongoing() is True
                assert ongoing_activity != device_validation_activity
                assert ongoing_activity == got_to_office_activity
                assert ongoing_activity is ongoing_activity
                assert got_to_office_activity is got_to_office_activity
                assert ongoing_activity is got_to_office_activity
                
                assert device_validation_activity.name == "On Device Validation"
                assert ongoing_activity.name == "Got to office"
                
                ongoing_activity_copy = work.ongoing_activity()
                assert ongoing_activity_copy is ongoing_activity
                
                log.debug('Activity.stop() -> Entry')
                got_to_office_last_entry: Entry = ongoing_activity.stop()
                assert isinstance(got_to_office_last_entry, Entry)
                assert got_to_office_last_entry
                assert got_to_office_last_entry.end
                
                assert ongoing_activity.ongoing() is False
                
                log.debug('Activity.stop() -> ValueError (not ongoing)')
                with assert_raises(ValueError, match=f"{ongoing_activity!r} is not ongoing"):
                    ongoing_activity.stop()
                
                log.debug('Work.ongoing_activity() -> ValueError (no ongoing activity)')
                with assert_raises(ValueError, match="No ongoing activity"):
                    work.ongoing_activity()
                
                log.debug('Work.on("Something New") -> Activity')
                something_new_activity: Activity = work.on("Something New")
                assert isinstance(something_new_activity, Activity)
                assert something_new_activity
                assert len(something_new_activity) == 1
                assert something_new_activity.name == "Something New"
                something_new_activity_is_ongoing = something_new_activity.ongoing()
                assert something_new_activity_is_ongoing is True
                assert device_validation_activity.name == "On Device Validation"
                assert ongoing_activity.name == "Got to office"
                assert device_validation_activity.ongoing() is False
                assert ongoing_activity.ongoing() is False
                
                log.debug('Activity.start() -> ValueError (already ongoing)')
                with assert_raises(ValueError, match=f"{something_new_activity!r} is already ongoing"):
                    something_new_activity.start()
                
                log.debug('Work.on("Something New") -> ValueError (already ongoing)')
                with assert_raises(ValueError, match=f"{something_new_activity!r} is already ongoing"):
                    work.on(something_new_activity.name)
                
                log.debug('Work.on("Something New2") -> Activity')
                something_new2_activity: Activity = work.on("Something New2")
                assert isinstance(something_new2_activity, Activity)
                assert something_new2_activity
                assert len(something_new2_activity) == 1
                assert something_new2_activity.name == "Something New2"
                assert something_new2_activity.ongoing() is True
                assert device_validation_activity.name == "On Device Validation"
                assert ongoing_activity.name == "Got to office"
                assert device_validation_activity.ongoing() is False
                assert ongoing_activity.ongoing() is False
                assert something_new_activity.ongoing() is False
                
                log.debug('Work.on("something-new 2") -> ValueError (has similar name)')
                assert something_new2_activity.has_similar_name("something-new 2") is True
                with assert_raises(ValueError,
                                   match=f"{something_new2_activity!r} is ongoing, and has a similar name to 'something-new 2"):
                    work.on("something-new 2")

                log.debug('Work.stop() -> Optional[Activity]')
                stop_time = XArrow.now()
                stopped_activity: Activity = work.stop(stop_time)
                assert stopped_activity.name == "Something New2"
                assert stopped_activity[-1].end == stop_time
                assert stopped_activity.ongoing() is False
                with assert_raises(ValueError, match=f"No ongoing activity"):
                    work.ongoing_activity()
                with assert_raises(ValueError, match=f"No ongoing activity"):
                    work.stop()
                
            
            def test_load_store(self, work=None):
                log.title(f"test_load_store({work = })")
                if not work:
                    work = default_work()
                with temp_sheet("/tmp/timefred-sheet-test_on_device_validation_08_30.toml"):
                    store.dump(work)
                    work = store.load()
                self.test_sanity(work=work)