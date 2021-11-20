from test.testutils import default_work
from timefred.log import log
from timefred.store import Day, Activity
from timefred.time import XArrow

test_start = XArrow.now()


def test_ongoing():
    log.title(f"test_features.test_ongoing()")
    work = default_work(test_start)
    day: Day = work[test_start.DDMMYY]
    got_to_office_activity: Activity = day["Got to office"]
    got_to_office_activity_is_ongoing = got_to_office_activity.ongoing()
    device_validation_activity: Activity = day["On Device Validation"]
    device_validation_activity_is_ongoing = device_validation_activity.ongoing()
    ongoing_activity: Activity = work.ongoing_activity()
    assert ongoing_activity is got_to_office_activity