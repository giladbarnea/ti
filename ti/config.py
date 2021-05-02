from typing import Optional

import toml
from pathlib import Path
from dataclasses import dataclass
from pytz import timezone, BaseTzInfo


@dataclass
class TimeCfg:
    tz: BaseTzInfo
    format: str

    def __init__(self, timecfg: dict):
        for k, v in timecfg.items():
            setattr(self, k, v)
        self.tz = timezone(self.tz)

    # def __post_init__(self):



@dataclass
class Config:
    time: Optional[TimeCfg]

    def __init__(self) -> None:
        cfg_file = Path.home() / '.timefred.toml'
        if cfg_file.exists():
            cfg = toml.load(cfg_file.open())
            self.time = TimeCfg(cfg.get("time"))
        else:
            self.time = None

    def __bool__(self):
        return self.time is not None


config = Config()
