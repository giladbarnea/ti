from os import path, getenv
from pathlib import Path
from typing import TypedDict, Optional
from subprocess import getstatusoutput
import yaml
from pdbpp import break_on_exc, rerun_and_break_on_exc

# @dataclass
# from timefred.util import timeit
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


class Store:

    def __init__(self, filename):
        self.filename = Path(filename)

    @rerun_and_break_on_exc
    def load(self) -> list[Entry]:  # perf: 150ms
        if self.filename.exists():
            with self.filename.open() as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                if not data:
                    data = []
        else:
            data = []
        return data

    @break_on_exc
    def dump(self, data: list[Entry]) -> bool:
        if getenv('TF_DRYRUN', "").lower() in ('1', 'true', 'yes'):
            print('\n\tDRY RUN, NOT DUMPING\n')
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
            print(f'Restored sheet backup')
            raise


from timefred.config import config

store = Store(path.expanduser(config.sheet.path))
