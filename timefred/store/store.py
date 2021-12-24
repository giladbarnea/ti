import logging
import os
import shutil
import sys
from os import path, getenv
from pathlib import Path

import toml

from timefred.singleton import Singleton
from timefred.space import Field, Space
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
class Store(Space):
    # cache: StoreCache = Field(default_factory=StoreCache)
    path: Path = Field(cast=Path)
    encoder: TomlEncoder = Field(default_factory=TomlEncoder)
    
    # def __init__(self, path):
    #     # self.encoder = TomlEncoder()
    #     self.path = Path(path)
    #     # super().__init__(path=Path(path))
    
    def load(self) -> Work:
        # perf: 150ms?
        # if self.cache.data:
        #     return self.cache.data
        
        if self.path.exists():
            with self.path.open() as f:
                data = toml.load(f)
            
            if not data:
                data = {}
        
        else:
            data = {}
            with self.path.open('w') as f:
                toml.load(data, f)
        # self.cache.data = data
        return Work(**data)
    
    def _backup(self, name_suffix='') -> bool:
        from timefred.config import config
        destination = (config.cache.path / self.path.name)
        destination_name = self.path.stem + name_suffix + '.backup'
        destination = destination.with_name(destination_name)
        try:
            shutil.copyfile(self.path, destination)
            return True
        except Exception as e:
            logging.error(f'Failed copying {self.path} to {destination}', exc_info=True)
            return False
    
    def _restore_from_backup(self, name_suffix='') -> bool:
        from timefred.config import config
        destination = (config.cache.path / self.path.name).with_name(self.path.stem + name_suffix + '.backup')
        try:
            shutil.move(destination, self.path)
            return True
        except Exception as e:
            logging.error(f'Failed moving {destination} to {self.path}', exc_info=True)
            return False
    
    def dump(self, data: Work) -> bool:
        if getenv('TIMEFRED_DRYRUN', "").lower() in ('1', 'true', 'yes'):
            print('\n\tDRY RUN, NOT DUMPING\n', data)
            return True
        
        if not self.path.exists():
            with self.path.open('w') as f:
                toml.dump({}, f, self.encoder)
        
        if not self._backup():
            return False
        try:
            with self.path.open('w') as f:
                toml.dump(data, f, self.encoder)
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            if self._restore_from_backup():
                print(f'Restored sheet backup', file=sys.stderr)
            raise

# breaks testutils.temp_sheet
# if os.getenv('TIMEFRED_NO_PROXIES', '').lower() in ('1', 'true'):
#     from timefred.config import config
#
#     store: Store = Store(path=path.expanduser(config.sheet.path))
# else:
class StoreProxy(Singleton):
    _store: Store = None
    
    def __getattr__(self, name):
        if name == '_store':
            return self._store
        if self._store is None:
            from timefred.config import config
            self._store = Store(path=path.expanduser(config.sheet.path))
        return getattr(self._store, name)


# noinspection PyTypeChecker
store: Store = StoreProxy()