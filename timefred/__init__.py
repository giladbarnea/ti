# This is so entrypoint "tf = timefred:main" can work
# from timefred.timefred import main

from contextlib import suppress

with suppress(ImportError):
    import os
    os.environ['DEBUGFILE_PATCH_PRINT'] = '1'
    import debug
    # from icecream import ic
    # ic.configureOutput(prefix='', includeContext=True)
    # from copy import deepcopy
    # import builtins
    # builtins.__print__ = deepcopy(print)
    # builtins.print = ic