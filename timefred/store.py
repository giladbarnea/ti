import logging
import shutil
import sys
from os import path, getenv
from pathlib import Path
from typing import Optional, Type, Any, Union, Iterable

import toml

from timefred import color as c
from timefred.color.colored import Colored, TaskString
from timefred.field import Field, UNSET
from timefred.space import DictSpace, DefaultDictSpace, TypedListSpace
from timefred.integration.jira import Ticket
from timefred.note import Note
from timefred.time import XArrow, Timespan
from timefred.util import normalize_str
from timefred.log import log

class Entry(DictSpace):
    start: XArrow = Field(cast=XArrow.from_formatted)
    end: Optional[XArrow] = Field(cast=XArrow.from_formatted, optional=True)
    notes: Optional[list[Note]] = Field(optional=True)
    tags: Optional[set[str]] = Field(optional=True)
    
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
    """Activity [Entry, Entry...]"""
    # name: Colored = Field(cast=lambda s: Colored(s, brush=c.task))
    name: Colored = Field(cast=TaskString)
    jira: Optional[Ticket] = Field(default_factory=Ticket)

    
    def __init__(self, iterable: Iterable = (), **kwargs) -> None:
        # Necessary because otherwise TypedSpace.__new__ expects (self, default_factory, **kwargs)
        super().__init__(iterable, **kwargs)

    def __repr__(self):
        representation = f'{self.__class__.__qualname__}(name={self.name!r}) {list.__repr__(self)}'
        # representation = f'{self.__class__.__qualname__} {list.__repr__(self)}'
        return representation

    # @multimethod
    # def has_similar_name(self, other: 'Entry') -> bool:
    #     return self.has_similar_name(other.name)
    #
    # @multimethod
    def has_similar_name(self, other: str) -> bool:
        return normalize_str(self.name) == normalize_str(other)
    
    def ongoing(self) -> bool:
        try:
            last_entry = self[-1]
            return not last_entry.end
        except IndexError:
            return False
    
    def stop(self, end: Union[XArrow, str] = None) -> XArrow:
        last_entry = self[-1]
        if last_entry.end:
            raise ValueError(f'{self!r} is not ongoing')
        if not end:
            end = XArrow.now()
        last_entry.end = end
        return last_entry.end
    
    
class Day(DefaultDictSpace[Any, Activity], default_factory=Activity):
    """Day { activity_name: Activity }"""
    __v_type__: Type[Activity]
    
    def __getitem__(self, name: Any) -> Activity:
        # log(f'[title]{self.__class__.__qualname__}.__getitem__({name!r})...')
        try:
            # Don't want the whole DefaultDictSpace->DefaultSpace.__getitem__(name) flow,
            # because we want self.__v_type__(name=name), and DefaultSpace does self.__v_type__()
            item = dict.__getitem__(self, name)
            # item = super(DictSpace).__getitem__(self, name)
            
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
            # log(f'  constructed = self.__v_type__(name={name!r})')
            constructed = self.__v_type__(name=name)
            # log(f'  {constructed = !r} | {constructed.name = !r}')
            assert constructed.name == name, f'{constructed.name = !r}, {name = !r}'
            # log(f'  setattr(self, {name!r}, {constructed!r})')
            # setattr(self, name, constructed)
        else:
            # log(f'  No KeyError',
            #     f'{item = !r}',
            #     f'self.__dict__.get({name!r}) = {self.__dict__.get(name)}',
            #     f'self.get({name!r}, UNSET) = {self.get(name, UNSET)}',
            #     f'{isinstance(item, self.__v_type__) = }',
            #     f'{item = !r}',
            #     f'{getattr(item, "name", UNSET) = !r}',
            #     sep='\n  ')
            if isinstance(item, self.__v_type__):
                constructed = item
            else:
                assert not isinstance(item, dict) # because __v_type__ expects pos arg, not **mapping
                constructed = self.__v_type__(item, name=name)
                assert constructed.name == name, f'{constructed.name=!r} != {name=!r} | {self.__class__.__qualname__}'
                # setattr(self, name, constructed)
        assert constructed.name == name, f'{constructed.name=!r} != {name=!r} | {self.__class__.__qualname__}'
        # log(f'{self.__class__.__qualname__}.__getitem__({name!r}) => {constructed!r}\n\n')
        return constructed

    def ongoing_activity(self) -> Optional[Activity]:
        for name in reversed(self.keys()):
            activity = self[name]   # invoke __getitem__ to get constructed
            if activity.ongoing():
                return activity
        return None

assert Day.__v_type__ == Activity
# class Work(DefaultDictSpace, default_factory=Day): ...
Work = DefaultDictSpace[str, Day]
'''{ "02/11/21" : Day }'''

assert Day.__v_type__ == Activity
# class StoreCache:
#     data: defaultdict[str, Day] = Field(default_factory=lambda **kwargs: defaultdict(Day, **kwargs))

class TomlEncoder(toml.TomlEncoder):
    def __init__(self, _dict=dict, preserve=False):
        super().__init__(_dict, preserve)
        self.dump_funcs.update({
            # DictSpace: dict,
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
        return DefaultDictSpace(Day, **data)
    
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

    # @eye
    def dump(self, data: Work) -> bool:
        if getenv('TF_DRYRUN', "").lower() in ('1', 'true', 'yes'):
            print('\n\tDRY RUN, NOT DUMPING\n',
                  data)
            
            return True
        
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
