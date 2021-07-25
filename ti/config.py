import os
from pathlib import Path
from typing import TypedDict

import toml
from pytz import timezone, BaseTzInfo

from ti.dikt import Dikt


class Config(Dikt):
	class TimeCfg(Dikt):
		class TimeFormats(Dikt):
			date: str = 'DD/MM/YY'
			short_date: str = 'DD/MM'
			date_time: str = 'DD/MM/YY HH:mm:ss'
			time: str = 'HH:mm:ss'

		tz: BaseTzInfo
		formats: TimeFormats

		def __init__(self, timecfg: dict):
			super().__init__(timecfg)
			self.tz = timezone(self.tz)

	time: TimeCfg
	sheet: Dikt = {"path": "~/.timefred-sheet.yml"}

	def __init__(self) -> None:
		cfg_file = Path.home() / '.timefred.toml'
		if cfg_file.exists():
			cfg = toml.load(cfg_file.open())
		else:
			cfg = {}
		super().__init__(cfg)
		if self.dev.debugger:
			os.environ['PYTHONBREAKPOINT'] = self.dev.debugger
		if self.dev.traceback:
			if self.dev.traceback == "rich.traceback":
				from rich.traceback import install
				install(show_locals=True)
			else:
				print(f'dont support {self.dev.traceback}')


config = Config()
