from timefred.color import Colored
from timefred.space import DefaultDictSpace
from timefred.store import Day, Entry, Activity
from timefred.time import XArrow


class TestEmptySheet:
    def test_on_got_to_office_08_20(self):
        work = DefaultDictSpace(Day)
        '''{ "02/11/21" : Day }'''
        assert isinstance(work, DefaultDictSpace)
        assert isinstance(work, dict)
        assert not work
        assert len(work) == 0
        entry = Entry(start="08:20")
        assert entry
        assert entry.start
        assert isinstance(entry.start, XArrow)
        assert repr(entry) != '{}'
        name = "Got to office"
        activity = Activity(name=name)
        assert not activity # because list
        assert len(activity) == 0
        assert isinstance(activity.name, Colored)
        assert activity.name == name
        activity.append(entry)
        assert activity
        assert len(activity) == 1
        assert activity[0] == entry
        day = work[entry.start.DDMMYY]
        assert isinstance(day, Day)
        day[activity.name] = activity
        assert day[str(activity.name)] == activity
        assert work
        assert len(work) == 1

class TestSheetWithContent:
    def test_on_device_validation_08_30(self):
        now = XArrow.now()
        sheet = {
            now.DDMMYY : {
                "Got to office" : [ { "start": "02:20" } ]
                }
            }
        work = DefaultDictSpace(Day, **sheet)
        assert isinstance(work, DefaultDictSpace)
        assert work
        assert len(work) == 1
        # time = XArrow.from_formatted("02/11/21 08:30")
        day = work[now.DDMMYY]
        assert isinstance(day, Day)
        assert len(day) == 1
        assert day
        name = "On Device Validation"
        device_validation_activity = day[name]
        assert isinstance(device_validation_activity, Activity)
        assert not device_validation_activity
        assert len(device_validation_activity) == 0
        assert repr(device_validation_activity) == f"Activity(name='{name}') []"
        assert isinstance(device_validation_activity.name, Colored)
        assert not device_validation_activity.ongoing()
        ongoing_activity = day.ongoing_activity()
        assert isinstance(ongoing_activity, Activity)
        assert ongoing_activity
        assert ongoing_activity.name == 'Got to office'
        assert isinstance(ongoing_activity.name, Colored)
        assert len(ongoing_activity) == 1
        assert ongoing_activity != device_validation_activity
        got_to_office_end_time = ongoing_activity.stop()
        assert isinstance(got_to_office_end_time, XArrow)
        
        
