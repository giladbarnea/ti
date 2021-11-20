import logging
import shutil
import sys
from collections import Mapping
from os import path, getenv
from pathlib import Path
from typing import Optional, Type, Any, Union, Iterable

import cheap_repr
import toml

from timefred.color.colored import Colored, TaskString
from timefred.integration.jira import Ticket
from timefred.note import Note
from timefred.space import AttrDictSpace, DefaultAttrDictSpace, TypedListSpace, Field
from timefred.tag import Tag
from timefred.time import XArrow, Timespan
from timefred.util import normalize_str


class Entry(AttrDictSpace):
    start: XArrow = Field(cast=XArrow.from_formatted)
    end: Optional[XArrow] = Field(cast=XArrow.from_formatted, optional=True)
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
    """Activity (name=...) [Entry, Entry...]"""
    # name: Colored = Field(cast=lambda s: Colored(s, brush=c.task))
    name: Colored = Field(cast=TaskString)
    jira: Optional[Ticket] = Field(default_factory=Ticket)
    
    def __init__(self, iterable: Iterable = (), **kwargs) -> None:
        # Necessary because otherwise TypedSpace.__new__ expects (self, default_factory, **kwargs)
        super().__init__(iterable, **kwargs)
    
    def __repr__(self):
        # representation = f'{self.__class__.__qualname__}(name={getattr(self, "name", "⟨UNSET⟩")!r} <{str(id(self))[-4:]}>) {list.__repr__(self)}'
        representation = f'{self.__class__.__qualname__}<{str(id(self))[-4:]}> {list.__repr__(self)}'
        return representation
    
    # @multimethod
    # def has_similar_name(self, other: 'Entry') -> bool:
    #     return self.has_similar_name(other.name)
    #
    # @multimethod
    def has_similar_name(self, other: str) -> bool:
        return normalize_str(self.name) == normalize_str(other)
    
    @eye
    def ongoing(self) -> bool:
        try:
            last_entry = self[-1]
            return not last_entry.end
        except IndexError:
            return False
    
    def stop(self, time: Union[XArrow, str] = None, tag=None, note=None) -> Entry:
        """
        Raises:
            ValueError: if the activity is not ongoing
        """
        last_entry = self[-1]
        if last_entry.end:
            raise ValueError(f'{self!r} is not ongoing')
        if not time:
            time = XArrow.now()
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
            raise ValueError(f'{self!r} is already ongoing')
        entry = Entry(start=time)
        if tag:
            entry.tags.add(tag)
        if note:
            entry.notes.append(note)
        
        self.append(entry)
        return entry


cheap_repr.register_repr(Activity)(cheap_repr.normal_repr)


# @register_repr(Activity)
# def Activity_repr(activity, helper: ReprHelper):
#     helper.level
# return repr(activity)

class Day(DefaultAttrDictSpace[Any, Activity], default_factory=Activity):
    """Day { activity_name: Activity }"""
    __default_factory__: Type[Activity]
    
    @eye
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
    
    @eye
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
        if time is None:
            time = XArrow.now()
        try:
            ongoing_activity = self.ongoing_activity()
        except ValueError:
            return None
        # TODO: ongoing_activity.stop() may raise ValueError/IndexError,
        #       how should be handled?
        ongoing_activity.stop(time=time, tag=tag, note=note)
        stopped_activity = ongoing_activity
        return stopped_activity
    
    def on(self,
           name: str,
           time: Union[str, XArrow] = None,
           tag: Union[str, Tag] = None,
           note: Union[str, Note] = None) -> Activity:
        
        if time is None:
            time = XArrow.now()
        try:
            ongoing_activity = self.ongoing_activity()
        except ValueError:
            pass
        else:
            if ongoing_activity.has_similar_name(name):
                raise ValueError(f'{ongoing_activity!r} is ongoing, and has a similar name to {name!r}')
            ongoing_activity.stop(time)
        finally:
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