import logging
import os
import shutil
import sys
from collections import Mapping
from os import path, getenv
from pathlib import Path
from typing import Optional, Type, Any, Union, Iterable

import toml

from timefred.color.colored import Colored, TaskString
from timefred.integration.jira import JiraTicket
from timefred.note import Note
from timefred.space import AttrDictSpace, DefaultAttrDictSpace, TypedListSpace, Field
from timefred.log import log
from timefred.tag import Tag
from timefred.time import XArrow, Timespan
from timefred.util import normalize_str


class Entry(AttrDictSpace):
    start: XArrow = Field(cast=XArrow.from_absolute)
    end: Optional[XArrow] = Field(cast=XArrow.from_absolute, optional=True)
    notes: Optional[list[Note]] = Field(optional=True)
    tags: Optional[set[Tag]] = Field(optional=True)
    
    # @Field(optional=True)
    @property
    def timespan(self):
        return Timespan(self.start, self.end)
    
    # def __init__(self, name, start, end=None, notes=None, tags=None, jira=None) -> None:
    # 	super().__init__(dict(name=name,
    # 						  start=start,
    # 						  end=end,
    # 						  notes=notes or [],
    # 						  tags=tags or set(),
    # 						  jira=jira))
    
    # @property
    # def notes(self) -> list[Note]:
    # 	if self.__cache__.notes:
    # 		return self._notes
    # 	for i, note in enumerate(self._notes):
    # 		if not isinstance(note, Note):
    # 			self._notes[i] = Note(note)
    # 	self.__cache__.notes = True
    # 	return self._notes
    
    # @property
    # def start(self) -> XArrow:
    # 	if self._start and not isinstance(self._start, Arrow):
    # 		self._start = XArrow.from_formatted(self._start)
    # 	return self._start
    
    # @start.setter
    # def start(self, val):
    # 	self._start = val
    
    # @property
    # def end(self) -> XArrow:
    # 	if self._end and not isinstance(self._end, Arrow):
    # 		self._end = XArrow.from_formatted(self._end)
    # 	return self._end
    #
    # @end.setter
    # def end(self, val):
    # 	self._end = val


class Activity(TypedListSpace[Entry], default_factory=Entry):
    """Activity (name=..., jira=...) [Entry, Entry...]"""
    name: Colored = Field(cast=TaskString)
    jira: Optional[JiraTicket] = Field(default_factory=JiraTicket)
    
    def __init__(self, iterable: Iterable = (), **kwargs) -> None:
        # Necessary because otherwise TypedSpace.__new__ expects (self, default_factory, **kwargs)
        super().__init__(iterable, **kwargs)
    
    def __repr__(self) -> str:
        name = f'{getattr(self, "name")}'
        short_id = f'{str(id(self))[-4:]}'
        jira = self.jira
        representation = f'{self.__class__.__qualname__} ({name=!r}, {jira=!r} <{short_id}>) {list.__repr__(self)}'
        return representation
    
    def shortrepr(self) -> str:
        """Like repr, but with only the last entry."""
        name = f'{getattr(self, "name")}'
        short_id = f'{str(id(self))[-4:]}'
        jira = self.jira
        last_entry = self._safe_last_entry()
        self_len = len(self)
        if self_len > 1:
            short_entries_repr = f'[... {last_entry}]'
        elif self_len == 1:
            short_entries_repr = f'[{last_entry}]'
        else:
            short_entries_repr = f'[]'
        representation = f'{self.__class__.__qualname__} ({name=!r}, {jira=!r} <{short_id}>) {short_entries_repr}'
        return representation
    
    def _safe_last_entry(self) -> Optional[Entry]:
        try:
            return self[-1]
        except IndexError:
            return None
    # @multimethod
    # def has_similar_name(self, other: 'Entry') -> bool:
    #     return self.has_similar_name(other.name)
    #
    # @multimethod
    def has_similar_name(self, other: str) -> bool:
        """Compares the activity's lowercase, stripped and non-word-free name to other."""
        return normalize_str(self.name) == normalize_str(other)
    
    def ongoing(self) -> bool:
        last_entry = self._safe_last_entry()
        return bool(last_entry and not last_entry.end)
    
    def stop(self,
             time: Union[str, XArrow] = None,
             tag: Union[str, Tag] = None,
             note: Union[str, Note] = None) -> Entry:
        """
        Raises:
            ValueError: if the activity is not ongoing
        """
        last_entry = self._safe_last_entry()
        if not last_entry or last_entry.end:
            raise ValueError(f'{self.shortrepr()} is not ongoing')
        if not time:
            time = XArrow.now()
        if last_entry.start > time:
            raise ValueError(f'Cannot stop {self.shortrepr()} before start time (tried to stop at {time!r})')
        last_entry.end = time
        
        if tag:
            last_entry.tags.add(tag)
        if note:
            last_entry.notes.append(note)
        return last_entry
    
    def start(self,
              time: Union[XArrow, str] = None,
              tag: Union["Tag", str] = None,
              note=None) -> Entry:
        """
        Raises:
            ValueError: if the activity is ongoing
        """
        if self.ongoing():
            raise ValueError(f'{self.shortrepr()} is already ongoing')
        entry = Entry(start=time)
        if tag:
            entry.tags.add(tag)
        if note:
            entry.notes.append(note)
        
        self.append(entry)
        return entry


if os.getenv('TIMEFRED_BIRDSEYE'):
    import cheap_repr
    
    cheap_repr.register_repr(Activity)(cheap_repr.normal_repr)


# @register_repr(Activity)
# def Activity_repr(activity, helper: ReprHelper):
#     helper.level
# return repr(activity)

class Day(DefaultAttrDictSpace[Any, Activity], default_factory=Activity):
    """Day { "activity_name": Activity }"""
    __default_factory__: Type[Activity]
    
    def __getitem__(self, name):
        # log(f'[title]{self.__class__.__qualname__}.__getitem__({name!r})...')
        try:
            # Don't want the whole DefaultAttrDictSpace->DefaultDictSpace->TypedDictSpace.__getitem__(name) flow,
            # because we want self.__default_factory__(name=name), and TypedDictSpace does self.__default_factory__()
            item = dict.__getitem__(self, name)
            # item = super(AttrDictSpace).__getitem__(self, name)
            
            # AttributeError: 'super' object has no attribute '__getitem__' error
            # item = super(dict, self).__getitem__(name)
            
            # AttributeError: 'super' object has no attribute '__getitem__' error
            # item = super(dict, self.__class__).__getitem__(name)
            
            # constructed = self.__dict__[name]
        except KeyError as e:
            # log(f'  KeyError: {e}',
            #     f'self.__dict__.get({name!r}) = {self.__dict__.get(name)}',
            #     f'self.get({name!r}, UNSET) = {self.get(name, UNSET)}',
            #     sep='\n  ')
            # log(f'  constructed = self.__default_factory__(name={name!r})')
            constructed = self.__default_factory__(name=name)
            # log(f'  {constructed = !r} | {constructed.name = !r}')
            # assert constructed.name == name, f'{constructed.name = !r}, {name = !r}'
            # log(f'  setattr(self, {name!r}, {constructed!r})')
            setattr(self, name, constructed)
        else:
            # log(f'  No KeyError',
            #     f'{item = !r}',
            #     f'self.__dict__.get({name!r}) = {self.__dict__.get(name)}',
            #     f'self.get({name!r}, UNSET) = {self.get(name, UNSET)}',
            #     f'{isinstance(item, self.__default_factory__) = }',
            #     f'{item = !r}',
            #     f'{getattr(item, "name", UNSET) = !r}',
            #     sep='\n  ')
            if isinstance(item, self.__default_factory__):
                constructed = item
            else:
                assert not isinstance(item, Mapping)  # because __default_factory__ expects pos arg, not **mapping
                constructed = self.__default_factory__(item, name=name)
                # assert constructed.name == name, f'{constructed.name=!r} != {name=!r} ({self.__class__.__qualname__})'
                setattr(self, name, constructed)
        # assert constructed.name == name, f'{constructed.name=!r} != {name=!r} ({self.__class__.__qualname__})'
        # log(f'{self.__class__.__qualname__}.__getitem__({name!r}) => {constructed!r}\n\n')
        return constructed


assert Day.__default_factory__ == Activity


class Work(DefaultAttrDictSpace[Any, Day], default_factory=Day):
    """Work { "31/10/21": Day }"""
    __default_factory__: Type[Day]
    
    def ongoing_activity(self) -> Activity:
        """
        Raises:
            ValueError: if there is no ongoing activity
        """
        # TODO: cache somehow
        for ddmmyy in reversed(self.keys()):
            day = self[ddmmyy]  # invoke __getitem__ to get constructed
            for name in reversed(day.keys()):
                activity = day[name]
                if activity.ongoing():
                    return activity
        raise ValueError(f'No ongoing activity')
    
    def stop(self,
             time: Union[str, XArrow] = None,
             tag: Union[str, Tag] = None,
             note: Union[str, Note] = None) -> Optional[Activity]:
        """
        Raises:
            ValueError: if there is no ongoing activity
        """
        ongoing_activity = self.ongoing_activity()
        if time is None:
            time = XArrow.now()
        ongoing_activity.stop(time=time, tag=tag, note=note)
        stopped_activity = ongoing_activity
        return stopped_activity
    
    def on(self,
           name: Union[str, Activity],
           time: Union[str, XArrow] = None,
           tag: Union[str, Tag] = None,
           note: Union[str, Note] = None) -> Activity:
        """
        Raises:
            ValueError: if an activity with the same / similar name is already ongoing
        """
        if time is None:
            time = XArrow.now()
        try:
            ongoing_activity = self.ongoing_activity()
        except ValueError:
            # No ongoing activity -> start new activity
            day = self[time.DDMMYY]
            activity: Activity = day[name]
            activity.start(time, tag, note)
            return activity
        else:
            # Ongoing activity -> stop it and start new activity
            if name == ongoing_activity.name:
                raise ValueError(f'{ongoing_activity.shortrepr()} is already ongoing')
            if ongoing_activity.has_similar_name(name):
                raise ValueError(f'{ongoing_activity.shortrepr()} is ongoing, and has a similar name to {name!r}')
            ongoing_activity.stop(time)
            day = self[time.DDMMYY]
            activity: Activity = day[name]
            activity.start(time, tag, note)
            return activity


assert Work.__default_factory__ == Day
assert Day.__default_factory__ == Activity
assert Work.__default_factory__ == Day
assert Day.__default_factory__ == Activity


# class StoreCache:
#     data: defaultdict[str, Day] = Field(default_factory=lambda **kwargs: defaultdict(Day, **kwargs))

class TomlEncoder(toml.TomlEncoder):
    def __init__(self, _dict=dict, preserve=False):
        super().__init__(_dict, preserve)
        self.dump_funcs.update({
            # AttrDictSpace: dict,
            # Colored: lambda colored: repr(str(colored)),
            XArrow: lambda xarrow: xarrow.HHmmss,
            })


# str:      Day {
#   str:        Activity[Entry, Entry, ...]
# {'26/10/21': {'Got to office': [{'start': '08:20:00'}]}}
# 24/10/21: {
#   Device exists redis validation: [
#       { name: str
#         start: 13:46:59
#         end?: 13:46:59
#         tags?: [...]
#         jira?: str
#         notes?: [...] },
#       { ... },
#   ]
class Store:
    # cache: StoreCache = Field(default_factory=StoreCache)
    filename: Path = Field(default_factory=Path, cast=Path)
    encoder: TomlEncoder = Field(default_factory=TomlEncoder)
    
    def __init__(self, filename):
        # self.filename = Path(filename)
        # self.encoder = TomlEncoder()
        self.filename = Path(filename)
        # super().__init__(filename=Path(filename))
    
    def load(self) -> Work:
        # perf: 150ms?
        # if self.cache.data:
        #     return self.cache.data
        
        if self.filename.exists():
            with self.filename.open() as f:
                data = toml.load(f)
            
            if not data:
                data = {}
        
        else:
            data = {}
            with self.filename.open('w') as f:
                toml.load(data, f)
        # self.cache.data = data
        return Work(**data)
    
    def _backup(self, name_suffix='') -> bool:
        try:
            shutil.copyfile(self.filename, f'{self.filename}{name_suffix}.backup')
            return True
        except Exception as e:
            logging.error(f'Failed copying {self.filename} to {self.filename}{name_suffix}.backup', exc_info=True)
            return False
    
    def _restore_from_backup(self, name_suffix='') -> bool:
        try:
            shutil.move(f'{self.filename}{name_suffix}.backup', self.filename)
            return True
        except Exception as e:
            logging.error(f'Failed moving {self.filename}{name_suffix}.backup to {self.filename}', exc_info=True)
            return False
    
    def dump(self, data: Work) -> bool:
        if getenv('TIMEFRED_DRYRUN', "").lower() in ('1', 'true', 'yes'):
            print('\n\tDRY RUN, NOT DUMPING\n',
                  data)
            
            return True
        
        if not self.filename.exists():
            with self.filename.open('w') as f:
                toml.dump({}, f, self.encoder)
        
        if not self._backup():
            return False
        try:
            with self.filename.open('w') as f:
                toml.dump(data, f, self.encoder)
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            if self._restore_from_backup():
                print(f'Restored sheet backup', file=sys.stderr)
            raise


from timefred.config import config

sheet = config.sheet
sheet_path = sheet.path
store = Store(path.expanduser(sheet_path))