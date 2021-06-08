from typing import Optional

import toml
from pathlib import Path
import os
from pytz import timezone, BaseTzInfo

from ti.dikt import Dikt


# @dataclass
class TimeCfg(Dikt):
    tz: BaseTzInfo
    format: str = 'MM/DD/YY'

    def __init__(self, timecfg: dict):
        super().__init__(timecfg)
        # for k, v in timecfg.items():
        #     setattr(self, k, v)
        self.tz = timezone(self.tz)

    # def __post_init__(self):



# @dataclass
class Config(Dikt):
    time: Optional[TimeCfg]
    def __init__(self, mapping=()) -> None:
        cfg_file = Path.home() / '.timefred.toml'
        if cfg_file.exists():
            cfg = toml.load(cfg_file.open())
            # time_cfg = cfg.get("time", {})
            # dev_cfg = cfg.get("dev", {})
        else:
            cfg = {}
            # time_cfg = {}
            # dev_cfg = {}
        super().__init__(cfg)
        if self.dev.debugger:
            os.environ['PYTHONBREAKPOINT'] = self.dev.debugger

        # self.time = TimeCfg(time_cfg)
        # self.dev = Dikt(dev_cfg)


config = Config()
