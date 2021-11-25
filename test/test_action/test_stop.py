from test.testutils import default_work, assert_raises
from timefred.store import Activity, Work, Entry


class TestEmptySheet:
    def test_empty_sheet(self):
        work = Work()
        
        with assert_raises(ValueError):
            work.ongoing_activity()


class TestSheetWithContent:
    class TestWithOngoingActivity:
        def test_sanity(self):
            work = default_work()
            ongoing_activity: Activity = work.ongoing_activity()
            assert ongoing_activity is not None
            assert ongoing_activity
            assert isinstance(ongoing_activity, Activity)
            assert ongoing_activity.name == "Got to office"
            assert len(ongoing_activity) == 1
            
            got_to_office_last_entry = ongoing_activity.stop()
            assert isinstance(got_to_office_last_entry, Entry)
            assert got_to_office_last_entry
            assert got_to_office_last_entry.end

            assert not ongoing_activity.ongoing()
            
