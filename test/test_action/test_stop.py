from test.testutils import default_work
from timefred.store import Activity, Work

class TestEmptySheet:
    def test_empty_sheet(self):
        work = Work()
        '''{ "02/11/21" : Day }'''
        
        ongoing_activity = work.ongoing_activity()
        assert ongoing_activity is None


class TestSheetWithContent:
    class TestWithOngoingActivity:
        def test_sanity(self):
            work = default_work()
            ongoing_activity = work.ongoing_activity()
            assert ongoing_activity is not None
            assert ongoing_activity
            assert isinstance(ongoing_activity, Activity)
            assert ongoing_activity.name == "Got to office"
            assert len(ongoing_activity) == 1
            
            got_to_office_end_time = ongoing_activity.stop()
