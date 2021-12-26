from test import TEST_START_ARROW
from test.testutils import default_work, assert_raises
from timefred.log import log
from timefred.note import Note
from timefred.store import Day, Activity, Entry
from timefred.tag import Tag
from timefred.time import XArrow
import pytest
import toml

class TestActivity:
    def test_ongoing(self):
        log.title(f"test_models.test_ongoing()")
        work = default_work(TEST_START_ARROW)
        day: Day = work.__getitem__(TEST_START_ARROW.DDMMYY)
        got_to_office_activity: Activity = day.__getitem__("Got to office")
        ongoing_activity: Activity = work.ongoing_activity()
        assert ongoing_activity is got_to_office_activity
        assert ongoing_activity.ongoing() is True
        assert got_to_office_activity.ongoing() is True
    
    class Test_timespans:
        ...
            
        
    class Test_stop:
        def test_stop_when_not_ongoing(self):
            log.title(f"test_models.test_stop_when_not_ongoing()")
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
            log.title(f"test_models.test_stop_before_last_entry_started()")
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
    
class TestEntry:
    def test_init_with_all_fields(self):
        entry = Entry(start="02:00:00",
                      end="03:00:00",
                      synced=True,
                      notes=[{"02:30:00": "PR-5000"}],
                      tags=["meeting"])
        assert entry
        assert entry.start == XArrow.from_absolute("02:00:00")
        assert entry.end == XArrow.from_absolute("03:00:00")
        assert entry.synced is True
        assert entry.notes
        assert isinstance(entry.notes, list)
        assert entry.notes == [Note({"02:30:00": "PR-5000"})]
        assert isinstance(entry.notes[0], Note)
        assert entry.notes[0] == Note({"02:30:00": "PR-5000"})
        assert entry.notes[0].time == XArrow.from_absolute("02:30:00")
        assert entry.notes[0].content == "PR-5000"
        assert entry.tags == [Tag("meeting")]
        assert next(iter(entry.tags)) == Tag("meeting")
        assert isinstance(next(iter(entry.tags)), Tag)
        
class TestDay:
    @pytest.mark.skip("not yet implemented")
    def test_new_structure(self):
        day = dict(start="10:00", end="19:00", Integration=dict(jira="ASM", sessions=[dict(start="10:10", end="18:50", synced=True)]))
        work = {"24/12/21": day}
        toml_str = toml.dumps(work)
        print(toml_str)
    