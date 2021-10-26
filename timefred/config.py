import os
import sys
from pathlib import Path
from typing import Optional

import toml
from pydantic import BaseModel, Field


class Config(BaseModel):
    class TimeCfg(BaseModel):
        class TimeFormats(BaseModel):
            date: str = 'DD/MM/YY'
            short_date: str = 'DD/MM'
            time: str = 'HH:mm:ss'

        # tz: BaseTzInfo
        # tz: datetime.timezone = dt.now().astimezone().tzinfo
        # tz: datetime.tzinfo = dt.now().astimezone().tzinfo
        tz = 'Asia/Jerusalem'
        formats: TimeFormats = Field(default_factory=TimeFormats)

        # def __init__(self, timecfg: dict):
        #     super().__init__(timecfg)
        # self.tz = timezone(self.tz)

    class DevCfg(BaseModel):
        debugger: Optional[str]
        traceback: Optional[str]
        features: Optional[BaseModel]

    class Sheet(BaseModel):
        path = os.path.expanduser(os.environ.get('TF_SHEET', "~/timefred-sheet.toml"))
    
    time: TimeCfg = Field(default_factory=TimeCfg)
    sheet: Sheet = Field(default_factory=Sheet)
    dev: Optional[DevCfg] = Field(default_factory=DevCfg)
    
    def __init__(self):
        cfg_file = Path(os.path.expanduser(os.environ.get('TF_CONFIG_PATH', "~/.timefred.toml")))
        
        if cfg_file.exists():
            cfg = toml.load(cfg_file.open())
        else:
            self._create_default_config_file(cfg_file)
            cfg = {}
        super().__init__(**cfg)
        if self.dev.debugger:
            os.environ['PYTHONBREAKPOINT'] = self.dev.debugger
        if self.dev.traceback:
            try:
                if self.dev.traceback == "rich.traceback":
                    from rich.traceback import install
                    install(show_locals=True)
                else:
                    print(f"Don't support {self.dev.traceback}", file=sys.stderr)
            except Exception as e:
                print(f'{e.__class__.__qualname__} caught in Config.__init__: {e}', file=sys.stderr)
    
    def _create_default_config_file(self, cfg_file: Path):
        constructed = self.construct().dict()
        toml.dump(constructed, cfg_file.open(mode="x"))

config = Config()
