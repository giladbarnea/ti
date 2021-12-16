import os
from timefred.store import store
from test import TEST_START_ARROW
from test.test_times import assert_arrows_soft_eq
from test.testutils import assert_raises, default_work, temp_sheet
from timefred.color import Colored
from timefred.store import Day, Activity, Work, Entry, store
from timefred.time import XArrow
from timefred.log import log
from timefred.action import log as log_action
from pytest import mark

@mark.skip("Not implemented yet")
def test_sanity():
    log.title(f"test_sanity()")
    work = default_work(TEST_START_ARROW)
    with temp_sheet("/tmp/timefred-sheet-test_log__test_sanity.toml"):
        store.dump(work)
        log_action()