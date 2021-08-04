import datetime
import os
import sys
from datetime import datetime as dt
from pathlib import Path
from typing import Optional

import toml

from timefred.dikt import Dikt


class Config(Dikt):
    class TimeCfg(Dikt):
        class TimeFormats(Dikt):
            date: str = 'DD/MM/YY'
            short_date: str = 'DD/MM'
            date_time: str = 'DD/MM/YY HH:mm:ss'
            time: str = 'HH:mm:ss'

        # tz: BaseTzInfo
        tz: datetime.timezone = dt.now().astimezone().tzinfo
        formats: TimeFormats

        # def __init__(self, timecfg: dict):
        #     super().__init__(timecfg)
        # self.tz = timezone(self.tz)

    class DevCfg(Dikt):
        debugger: Optional[str]
        traceback: Optional[str]
        features: Dikt

    time: TimeCfg
    sheet: Dikt = Dikt({"path": os.path.expanduser(os.environ.get('TF_SHEET', "~/.timefred-sheet.yml"))})
    dev: DevCfg

    def __init__(self) -> None:
        cfg_file = Path(os.path.expanduser(os.environ.get('TF_CONFIG', "~/.timefred.toml")))
        if cfg_file.exists():
            cfg = toml.load(cfg_file.open())
        else:
            cfg = {}
        super().__init__(cfg)
        if self.dev.debugger:
            os.environ['PYTHONBREAKPOINT'] = self.dev.debugger
        if self.dev.traceback:
            try:
                if self.dev.traceback == "rich.traceback":
                    from rich.traceback import install
                    install(show_locals=True)
                else:
                    print(f"Don't support {self.dev.traceback}")
            except Exception as e:
                print(f'{e.__class__.__qualname__} caught in Config.__init__: {e}', file=sys.stderr)


config = Config()
