import sys
from os import path, getenv
from pathlib import Path
from subprocess import getstatusoutput
from typing import TypedDict, Optional

import yaml
from pdbpp import break_on_exc

# @dataclass
# from timefred.util import timeit
from timefred.dikt import DefaultDikt

Entry = TypedDict('Entry', {
    'name':  str,
    'start': str,
    'end':   Optional[str],
    'notes': Optional[list[str]],
    'jira':  Optional[str],
    },
                  total=False)


class Data(dict):
    # doesn't write well to .timefred-sheet
    pass


# work: List[Item]
# interrupt_stack: List


class Store(DefaultDikt):

    def __init__(self, filename):
        self.filename = Path(filename)

    # @rerun_and_break_on_exc
    def load(self) -> list[Entry]:  # perf: 150ms
        if self.__cache__.data:
            return self.__cache__.data

        if self.filename.exists():
            with self.filename.open() as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

            if not data:
                data = []

        else:
            data = []
            with self.filename.open('w') as f:
                yaml.dump(data, f)

        self.__cache__.data = data
        return data

    @break_on_exc
    def dump(self, data: list[Entry]) -> bool:
        if getenv('TF_DRYRUN', "").lower() in ('1', 'true', 'yes'):
            print('\n\tDRY RUN, NOT DUMPING\n', file=sys.stderr)
            return False

        getstatusoutput(f'cp {self.filename} {self.filename}.backup')
        try:
            with self.filename.open('w') as f:
                yaml.dump(data, f, indent=4)
            return True
        except Exception as e:
            import logging
            logging.error(e, exc_info=True)
            getstatusoutput(f'mv {self.filename}.backup {self.filename}')
            print(f'Restored sheet backup', file=sys.stderr)
            raise


from timefred.config import config

store = Store(path.expanduser(config.sheet.path))
