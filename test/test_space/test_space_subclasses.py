from timefred.note import Note
from timefred.time import XArrow
import pytest

class TestNote:
    # @pytest.mark.skip('doesnt work')
    def test_sanity(self):
        note = Note({"17:00": "PR-6091"})
        assert isinstance(note.time, XArrow)
        assert note.time == XArrow.from_absolute("17:00")
        assert note.content == "PR-6091"