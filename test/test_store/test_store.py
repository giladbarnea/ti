import os
from timefred.store import store
from timefred.log import log
from test.testutils import assert_raises, default_work
from contextlib import contextmanager
from timefred.config import config

@contextmanager
def sheet_path(path, rm=False):
    old_path = config.sheet.path
    if os.environ['TIMEFRED_SHEET'] != old_path != store.filename:
        raise ValueError(f"Sheet path config mismatch: "
                         f"{os.environ['TIMEFRED_SHEET'] = !r}, {config.sheet.path = !r}, {store.filename = !r}")
    os.environ['TIMEFRED_SHEET'] = path
    config.sheet.path = path
    store.filename = path
    
    try:
        yield
    finally:
        os.environ['TIMEFRED_SHEET'] = old_path
        config.sheet.path = old_path
        store.filename = old_path
        if rm:
            if os.path.exists(path):
                os.remove(path)
class TestStore:
    def test_dump(self):
        work = default_work()
        log.title(f"test_load_store({work = })")
        os.environ['TIMEFRED_SHEET'] = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
        config.sheet.path = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
        store.filename = "/tmp/timefred-sheet-test_on_device_validation_08_30.toml"
    
        store.dump(work)
    
        log.debug('work = store.load()')
        work = store.load()
