from test.testutils import default_work, temp_sheet
from timefred.log import log
from timefred.space.field import UNSET
from timefred.store import store, Day, Activity, Entry
from timefred.time import XArrow


class TestStore:
    class TestLoad:
        def test_empty_sheet(self):
            ...
        
        def test_empty_day(self):
            ...

        def test_inline_activity__time_in_proper(self):
            raw_data = '["02/12/21"]\n"Got to office" = 09:40:00'
            sheet_path = '/tmp/timefred-sheet--test-store--test-load--test-inline-activity--time-in-proper.toml'
            with open(sheet_path, 'w') as sheet:
                sheet.write(raw_data)

            with temp_sheet(sheet_path):
                work = store.load()
            day: Day = work['02/12/21']
            activity: Activity = day['Got to office']
            entry: Entry = activity.safe_last_entry()
            assert isinstance(entry.start, XArrow)
            assert entry.start.HHmmss == "09:40:00"
            assert entry.end is UNSET
            
        def test_inline_activity__time_in_str(self):
            raw_data = '["02/12/21"]\n"Got to office" = "09:40"'

            sheet_path = '/tmp/timefred-sheet--test-store--test-load--test-inline-activity--time-in-str.toml'
            with open(sheet_path, 'w') as sheet:
                sheet.write(raw_data)

            with temp_sheet(sheet_path):
                work = store.load()
            day: Day = work['02/12/21']
            activity: Activity = day['Got to office']
            entry: Entry = activity.safe_last_entry()
            assert isinstance(entry.start, XArrow)
            assert entry.start.HHmmss == "09:40:00"
            assert entry.end is UNSET

        def test_subtable_activity__time_in_proper(self):
            raw_data = '["02/12/21"]\n[["02/12/21"."Got to office"]]\nstart = 09:40:00'
            sheet_path = '/tmp/timefred-sheet--test-store--test-load--test-subtable-activity--time-in-proper.toml'
            with open(sheet_path, 'w') as sheet:
                sheet.write(raw_data)
    
            with temp_sheet(sheet_path):
                work = store.load()
            day: Day = work['02/12/21']
            activity: Activity = day['Got to office']
            entry: Entry = activity.safe_last_entry()
            assert isinstance(entry.start, XArrow)
            assert entry.start.HHmmss == "09:40:00"
            assert entry.end is UNSET
    
    def test_dump(self):
        work = default_work()
        log.title(f"test_dump({work = })")
        # os.environ['TIMEFRED_SHEET'] = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
        # config.sheet.path = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
        # store.path = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
        with temp_sheet("/tmp/timefred-sheet-test_on_device_validation_08_30.toml"):
            store.dump(work)
            work = store.load()