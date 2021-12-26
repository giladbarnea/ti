from timefred.note import Note
from timefred.time import XArrow
from test import TEST_START_ARROW
import os
class TestNote:
    def test_sanity(self):
        note = Note({"17:00": "PR-6091"})
        assert isinstance(note.time, XArrow)
        assert note.time == XArrow.from_absolute("17:00")
        assert note.time.hour == 17
        assert note.time.minute == 0
        assert note.time.second == 0, note.time.second
        assert note.content == "PR-6091"
        if not os.getenv('TIMEFRED_REPR', '').lower() in ('no', 'disable'):
            assert repr(note) == f"Note(content = 'PR-6091', time = XArrow ⟨{TEST_START_ARROW.DDMMYY} 17:00:00⟩)", repr(note)