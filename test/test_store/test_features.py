from test.testutils import default_work
from timefred.log import log
from timefred.store import Day, Activity
from timefred.time import XArrow

test_start = XArrow.now()

@eye
def test_ongoing():
    log.title(f"test_features.test_ongoing()")
    work = default_work(test_start)
    day: Day = work.__getitem__(test_start.DDMMYY)
    got_to_office_activity: Activity = day.__getitem__("Got to office")
    ongoing_activity: Activity = work.ongoing_activity()
    assert ongoing_activity is got_to_office_activity
    assert ongoing_activity.ongoing() is True
    assert got_to_office_activity.ongoing() is True
