from test.testutils import default_work, sheet_path
from timefred.log import log
from timefred.store import store


class TestStore:
    def test_dump(self):
        work = default_work()
        log.title(f"test_dump({work = })")
        # os.environ['TIMEFRED_SHEET'] = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
        # config.sheet.path = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
        # store.path = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
        with sheet_path("/tmp/timefred-sheet-test_on_device_validation_08_30.toml"):
            store.dump(work)
            log.debug('work = store.load()')
            work = store.load()