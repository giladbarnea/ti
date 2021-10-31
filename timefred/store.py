import logging
import shutil
import sys
from os import path, getenv
from pathlib import Path
from typing import Optional

import toml

from timefred import color as c
from timefred.color.colored import Colored
from timefred.field import Field
from timefred.has_fields import HasFieldsDict, HasFieldsList, HasFieldsDefaultDict, K, V
from timefred.integration.jira import Ticket
from timefred.note import Note
from timefred.time import XArrow, Timespan
from timefred.util import normalize_str


class Entry(HasFieldsDict):
    start: XArrow = Field(caster=XArrow.from_formatted)
    end: Optional[XArrow] = Field(caster=XArrow.from_formatted, optional=True)
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


class Activity(HasFieldsList):
    name: Colored = Field(caster=lambda s: Colored(s, brush=c.task))
    jira: Optional[Ticket] = Field(default_factory=Ticket)
    
    # __slots__ = ('name',)
    
    # @multimethod
    # def has_similar_name(self, other: 'Entry') -> bool:
    #     return self.has_similar_name(other.name)
    #
    # @multimethod
    def has_similar_name(self, other: str) -> bool:
        return normalize_str(self.name) == normalize_str(other)
    
    def ongoing(self) -> bool:
        try:
            return not self[-1].end
        except IndexError:
            return False

    def __repr__(self):
        representation = f'{self.__class__.__qualname__}(name={self.name!r}) {list.__repr__(self)}'
        return representation

    
# Day = defaultdict[str, Activity]
# class Day(UserDict[str, Activity]):
class Day(HasFieldsDefaultDict, default_factory=Activity):
    """activity name : Activity"""

    def __getitem__(self, k: K) -> V:
        try:
            # Don't want the whole HasFieldsDefaultDict.__getitem__(k) flow
            constructed = dict.__getitem__(self, k)
        except KeyError as e:
            constructed = self.__v_type__(name=k)
            setattr(self, k, constructed)
        else:
            if not isinstance(constructed, self.__v_type__):
                constructed = self.__v_type__(**constructed)
                setattr(self, k, constructed)
        return constructed


assert Day.__v_type__ == Activity
# class Work(HasFieldsDefaultDict, default_factory=Day): ...
Work = HasFieldsDefaultDict[str, Day]
assert Day.__v_type__ == Activity
# class StoreCache:
#     data: defaultdict[str, Day] = Field(default_factory=lambda **kwargs: defaultdict(Day, **kwargs))

class TomlEncoder(toml.TomlEncoder):
    def __init__(self, _dict=dict, preserve=False):
        super().__init__(_dict, preserve)
        self.dump_funcs.update({
            # HasFieldsDict: dict,
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
    filename: Path = Field(default_factory=Path)
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
        return HasFieldsDefaultDict(Day, **data)
    
    def _backup(self) -> bool:
        try:
            shutil.copyfile(self.filename, f'{self.filename}.backup')
            return True
        except Exception as e:
            logging.error(f'Failed copying {self.filename} to {self.filename}.backup', exc_info=True)
            return False
    
    def _restore_from_backup(self) -> bool:
        try:
            shutil.move(f'{self.filename}.backup', self.filename)
            return True
        except Exception as e:
            logging.error(f'Failed moving {self.filename}.backup to {self.filename}', exc_info=True)
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
            # pp(data)
            with self.filename.open('w') as f:
                toml.dump(data, f, self.encoder)
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            if self._restore_from_backup():
                print(f'Restored sheet backup', file=sys.stderr)
            raise


from timefred.config import config

store = Store(path.expanduser(config.sheet.path))
