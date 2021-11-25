import os
import re
import sys
from pathlib import Path
from typing import Optional, Literal

import toml
# from pydantic import BaseModel, Field
from timefred.space.field import Field
from timefred.space import AttrDictSpace
from timefred.log import log


class Config(AttrDictSpace):
    class TimeCfg(AttrDictSpace):
        class TimeFormats(AttrDictSpace):
            date: str = 'DD/MM/YY'
            short_date: str = 'DD/MM'
            time: str = 'HH:mm:ss'
            short_time: str = 'HH:mm'
            datetime: str = f'{date} {time}'  # DD/MM/YY HH:mm:ss
            shorter_datetime: str = f'{date} {short_time}'  # DD/MM/YY HH:mm
            short_datetime: str = f'{short_date} {short_time}'  # DD/MM HH:mm

            def __init__(self, mappable=(), **kwargs) -> None:
                super().__init__(mappable, **kwargs)
                self.date_separator = re.search(r'[^\w]', self.date).group()  # e.g '/'
                self.time_separator = re.search(r'[^\w]', self.time).group()  # e.g ':'
                
                if self.date.count(self.date_separator) != 2:
                    raise ValueError(f'Invalid date format: {self.date!r}. Needs to signify Day, Month and Year.')
                if self.short_date.count(self.date_separator) != 1:
                    raise ValueError(f'Invalid date format: {self.short_date!r}. Needs to signify Day and Month.')
                if self.time.count(self.time_separator) != 2:
                    raise ValueError(f'Invalid date format: {self.time!r}. Needs to signify Hours, minutes and seconds.')
                if self.short_time.count(self.time_separator) != 1:
                    raise ValueError(f'Invalid date format: {self.short_time!r}. Needs to signify Hours and minutes.')
                
                self.time_format_re = re.compile(fr'(?P<hour>\d{{1,2}})(?:{self.time_separator}(?P<minute>\d{{2}})(?:{self.time_separator}(?P<second>\d{{2}}))?)?')
                """23[:31[:56]]"""

        # tz: BaseTzInfo
        # tz: datetime.timezone = dt.now().astimezone().tzinfo
        # tz: datetime.tzinfo = dt.now().astimezone().tzinfo
        # tz = timezone(self.tz)
        # TODO: have a tzinfo that can by psased to XArrow.now()
        tz = 'Asia/Jerusalem'
        first_day_of_week: Literal['sunday', 'monday'] = Field(cast=str.lower)
        formats: TimeFormats = Field(default_factory=TimeFormats, cast=TimeFormats)


    class DevCfg(AttrDictSpace):
        debugger: Optional[str] = Field(default_factory=str)
        traceback: Optional[str]= Field(default_factory=str)
        repr: Optional[str] = Field(default=repr)
        # features: Optional[BaseModel]

    class Sheet(AttrDictSpace):
        path = os.path.expanduser(os.environ.get('TIMEFRED_SHEET', "~/timefred-sheet.toml"))
    
    time: TimeCfg = Field(default_factory=TimeCfg, cast=TimeCfg)
    sheet: Sheet = Field(default_factory=Sheet, cast=Sheet)
    dev: Optional[DevCfg] = Field(default_factory=DevCfg, cast=DevCfg)
    
    def __init__(self):
        cfg_file = Path(os.path.expanduser(os.environ.get('TIMEFRED_CONFIG_PATH', "~/.timefred.toml")))
        
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
                    log.warning(f"Don't support {self.dev.traceback}")
            except Exception as e:
                log.error(f'{e.__class__.__qualname__} caught in {self}.__init__: {e}')
                
    def _create_default_config_file(self, cfg_file: Path):
        raise NotImplementedError
        constructed = self.dict()
        toml.dump(constructed, cfg_file.open(mode="x"))

config = Config()
