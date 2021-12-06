import logging
import shutil
import sys
from os import path, getenv
from pathlib import Path

import toml

from timefred.singleton import Singleton
from timefred.space import Field
from timefred.store import Work
from timefred.time import XArrow


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


class StoreProxy(Singleton):
    _store: Store = None
    
    def __getattr__(self, name):
        if self._store is None:
            from timefred.config import config
            self._store = Store(path.expanduser(config.sheet.path))
        return getattr(self._store, name)


# noinspection PyTypeChecker
store: Store = StoreProxy()