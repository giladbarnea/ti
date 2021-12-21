from test import TEST_START_ARROW
from test.testutils import default_work, temp_sheet  # , assert_raises
from timefred.action import log as log_action
from timefred.log import log
from timefred.store import store  # , Day, Activity, Work, Entry
from timefred.color import decolor
from textwrap import dedent

from timefred.time import XArrow


def test_sanity():
    log.title(f"test_sanity()")
    work = default_work(TEST_START_ARROW)
    work.stop()
    with temp_sheet("/tmp/timefred-sheet-test_log__test_sanity.toml"):
        store.dump(work)
        log_action()
        
def test_log_01_12_21(capsys):
    raw_data = dedent('''
    ["01/12/21"]
    "Got to office" = "10:00"
    
    [["01/12/21"."Integration"]]
    synced = true
    start = 10:30:00
    end = 11:00:00
    
    [["01/12/21"."Integration"]]
    synced = true
    start = 11:20:00
    end = 11:40:00
    
    [["01/12/21"."Integration - Weak WIFI Password"]]
    synced = true
    start = 13:30:00
    end = 13:40:00
    notes = {"13:40:00" = "With Vlad, tested, done, everything as expected"}
    
    [["01/12/21"."immediate endTime quiet time default value is empty str"]]
    start = 14:00:00
    end = 17:30:00
    jira = "ASM-13925"
    synced = true
    ''')
    sheet_path = '/tmp/timefred-sheet--test-action--test-log--test-log-01-12-21.toml'
    with open(sheet_path, 'w') as sheet:
        sheet.write(raw_data)

    with temp_sheet(sheet_path):
        log_action('01/12/21')

    captured = capsys.readouterr()
    output = captured.out
    output_lines = output.splitlines()
    now = XArrow.now()
    past = XArrow.from_absolute('01/12/21')
    from timefred.time.timeutils import arrows2rel_time
    assert decolor(output_lines[0]) == f'Wednesday, 01/12/21 | {arrows2rel_time(now, past)}'