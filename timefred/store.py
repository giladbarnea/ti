from os import path, getenv
from typing import TypedDict, Optional

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
        self.filename = filename

    @break_on_exc
    def load(self) -> list[Entry]:  # perf: 150ms
        if path.exists(self.filename):
            with open(self.filename) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                if not data:
                    data = []

        else:
            data = []
        return data

    @rerun_and_break_on_exc
    def dump(self, data: list[Entry]) -> bool:
        if getenv('TF_DRYRUN', "").lower() in ('1', 'true', 'yes'):
            print('\n\tDRY RUN, NOT DUMPING\n')
            return False
        with open(self.filename, 'w') as f:
            # json.dump(data, f, separators=(',', ': '), indent=2)
            yaml.dump(data, f, indent=4)
            return True


from timefred.config import config

store = Store(path.expanduser(config.sheet.path))
