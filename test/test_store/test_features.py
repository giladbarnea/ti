from test import TEST_START_ARROW
from test.testutils import default_work, assert_raises
from timefred.log import log
from timefred.store import Day, Activity, Entry
from timefred.time import XArrow

def test_ongoing():
    log.title(f"test_features.test_ongoing()")
    work = default_work(TEST_START_ARROW)
    day: Day = work.__getitem__(TEST_START_ARROW.DDMMYY)
    got_to_office_activity: Activity = day.__getitem__("Got to office")
    ongoing_activity: Activity = work.ongoing_activity()
    assert ongoing_activity is got_to_office_activity
    assert ongoing_activity.ongoing() is True
    assert got_to_office_activity.ongoing() is True



class TestStop:
    def test_stop_when_not_ongoing(self):
        log.title(f"test_features.test_stop_when_not_ongoing()")
        work = default_work(TEST_START_ARROW)
        day: Day = work.__getitem__(TEST_START_ARROW.DDMMYY)
        got_to_office_activity: Activity = day.__getitem__("Got to office")
        assert got_to_office_activity.ongoing() is True
        
        now = XArrow.now()
        entry: Entry = got_to_office_activity.stop(now)
        assert entry is got_to_office_activity.safe_last_entry()
        assert entry.end == now
        
        assert got_to_office_activity.ongoing() is False
        
        with assert_raises(ValueError, f'{got_to_office_activity} is not ongoing'):
            got_to_office_activity.stop()

    def test_stop_before_last_entry_started(self):
        log.title(f"test_features.test_stop_before_last_entry_started()")
        work = default_work(TEST_START_ARROW)
        
        day: Day = work.__getitem__(TEST_START_ARROW.DDMMYY)
        assert work[TEST_START_ARROW.DDMMYY] is day
        
        got_to_office_activity: Activity = day.__getitem__("Got to office")
        assert got_to_office_activity.ongoing() is True
        assert day['Got to office'] is got_to_office_activity
        
        last_entry: Entry = got_to_office_activity[-1]
        assert got_to_office_activity.safe_last_entry() is last_entry
        
        yesterday = XArrow.dehumanize('yesterday')
        with assert_raises(ValueError, f'Cannot stop {got_to_office_activity.shortrepr()} before start time (tried to stop at {yesterday!r})'):
            got_to_office_activity.stop(yesterday)
    
