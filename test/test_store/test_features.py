from test.testutils import default_work, assert_raises
from timefred.log import log
from timefred.store import Day, Activity, Entry
from timefred.time import XArrow

test_start = XArrow.now()

def test_ongoing():
    log.title(f"test_features.test_ongoing()")
    work = default_work(test_start)
    day: Day = work.__getitem__(test_start.DDMMYY)
    got_to_office_activity: Activity = day.__getitem__("Got to office")
    ongoing_activity: Activity = work.ongoing_activity()
    assert ongoing_activity is got_to_office_activity
    assert ongoing_activity.ongoing() is True
    assert got_to_office_activity.ongoing() is True


class TestStop:
    def test_stop_when_not_ongoing(self):
        log.title(f"test_features.test_stop_when_not_ongoing()")
        work = default_work(test_start)
        day: Day = work.__getitem__(test_start.DDMMYY)
        got_to_office_activity: Activity = day.__getitem__("Got to office")
        assert got_to_office_activity.ongoing()
        got_to_office_activity.stop()
        with assert_raises(ValueError):
            got_to_office_activity.stop()

    def test_stop_before_last_entry_started(self):
        log.title(f"test_features.test_stop_before_last_entry_started()")
        work = default_work(test_start)
        log.debug(f'{work = !r}')
        day: Day = work.__getitem__(test_start.DDMMYY)
        got_to_office_activity: Activity = day.__getitem__("Got to office")
        assert got_to_office_activity.ongoing()
        last_entry: Entry = got_to_office_activity[-1]
        log.debug(f'{ last_entry = !r}')
        log.debug(f'{ last_entry.start = !r}')
        with assert_raises(ValueError, "Cannot stop"):
            got_to_office_activity.stop('yesterday')
    
