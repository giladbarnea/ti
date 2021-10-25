import logging
import shutil
import sys
from collections import defaultdict
from os import path, getenv
from pathlib import Path
from typing import Optional, Any, ForwardRef

import toml

from timefred import color as c
from timefred.color.colored import Colored
from timefred.field import Field
from timefred.note import Note
from timefred.time import XArrow, Timespan
from timefred.util import normalize_str


# @dataclass
# from timefred.util import timeit


class Entry:
    # class Config:
    #     arbitrary_types_allowed = True
    
    # name_colored: str = Field(default_factory=lambda: c.task(Entry.name))
    name: Colored = Colored(brush=c.task)
    start: XArrow = Field(caster=XArrow.from_formatted)
    end: Optional[XArrow] = Field(caster=XArrow.from_formatted, optional=True)
    notes: Optional[list[Note]] = Field(optional=True)
    tags: Optional[set[str]] = Field(optional=True)
    jira: Optional[str] = Field(default_factory=str)
    
    @Field
    def timespan(self):
        return Timespan(self.start, self.end)
    
    def __new__(cls, *args: Any, **kwargs: Any):
        inst = object.__new__(cls)
        for name, val in kwargs.items():
            setattr(inst, name, val)
        # for item, annotation in cls.__annotations__.items():
        #     if isinstance(annotation, ForwardRef):
        #         raise NotImplementedError(f"{annotation = }")
        #         evaluated = resolve_forwardref(annotation, cls)
        #         cls.__annotations__[item] = evaluated
        
        return inst
    
    @classmethod
    def from_entry(cls, entry: dict) -> ForwardRef('Entry'):
        name = next(iter(entry))
        return cls(name=name, **entry[name])
    
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
    
    # @multimethod
    # def has_similar_name(self, other: 'Entry') -> bool:
    #     return self.has_similar_name(other.name)
    #
    # @multimethod
    def has_similar_name(self, other: str) -> bool:
        return normalize_str(self.name) == normalize_str(other)
    
    def dict(self, *, exclude=()):
        if not isinstance(exclude, tuple):
            exclude = (exclude,)
        attrs = {}
        for k in self.__annotations__:
            if k in exclude:
                continue
            v = getattr(self, k)
            if v:
                # with suppress(AttributeError):
                #     attrs[k] = v.HHmmss
                #     continue
                #
                # with suppress(AttributeError):
                #     attrs[k] = v.dict()
                #     continue
                
                attrs[k] = v
        
        return attrs


class Day:
    entries: list[Entry]


class StoreCache:
    data: dict[str, Day] = Field(default_factory=lambda **kwargs: defaultdict(Day, **kwargs))
    # class Config:
    #     arbitrary_types_allowed = True


class TomlEncoder(toml.TomlPreserveInlineDictEncoder):
    def __init__(self, _dict=dict):
        super().__init__(_dict)
        self.dump_funcs.update({
            Colored: lambda colored: repr(str(colored)),
            XArrow:  lambda xarrow: xarrow.HHmmss,
            })


class Store:
    cache: StoreCache = Field(default_factory=StoreCache)
    filename: Path = Field(default_factory=Path)
    encoder: TomlEncoder = Field(default_factory=TomlEncoder)
    
    def __init__(self, filename):
        # self.filename = Path(filename)
        # self.encoder = TomlEncoder()
        self.filename = Path(filename)
        # super().__init__(filename=Path(filename))
    
    # @rerun_and_break_on_exc
    def load(self) -> defaultdict[str, list[Entry]]:
        # perf: 150ms?
        if self.cache.data:
            return self.cache.data
        
        if self.filename.exists():
            with self.filename.open() as f:
                data = toml.load(f)
                # data = yaml.load(f, Loader=yaml.FullLoader)
            
            if not data:
                data = defaultdict(list)
        
        else:
            data = defaultdict(list)
            with self.filename.open('w') as f:
                toml.dump(data, f)
                # yaml.dump(data, f)
        
        self.cache.data = data
        return data
    
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
    
    # @break_on_exc
    def dump(self, data: defaultdict[str, Entry]) -> bool:
        if getenv('TF_DRYRUN', "").lower() in ('1', 'true', 'yes'):
            print('\n\tDRY RUN, NOT DUMPING\n', file=sys.stderr)
            return False
        
        if not self._backup():
            return False
        try:
            with self.filename.open('w') as f:
                # yaml.dump(data, f, indent=4)
                toml.dump(data, f, self.encoder)
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            if self._restore_from_backup():
                print(f'Restored sheet backup', file=sys.stderr)
            raise


from timefred.config import config

store = Store(path.expanduser(config.sheet.path))
