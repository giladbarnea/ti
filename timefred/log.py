class LazyConsole:
    def __get__(self, instance, owner):
        import sys
        import os
        from rich.console import Console
        from rich.theme import Theme
        theme = {
            'debug':   'dim',
            'warn':    'yellow',
            'warning': 'yellow',
            'error':   'red',
            'fatal':   'bright_red',
            'success': 'green',
            'prompt':  'b bright_cyan',
            'title':   'b bright_white',
            }
        console = Console(#force_terminal=True,
                          log_time_format='[%d.%m.%Y][%T]',
                          color_system='standard',
                          tab_size=2,
                          log_path=False,
                          file=sys.stdout if os.getenv('PYCHARM_HOSTED') else sys.stderr,
                          theme=Theme({**theme, **{k.upper(): v for k, v in theme.items()}}))
        if console.width == 80:
            console.width = 160
        return console


class LogProxy:
    console = LazyConsole()
    _log = None
    
    def __call__(self, *args, **kwargs):
        if self._log:
            return self._log(*args, **kwargs)
        _log = self.console.log
        self._log = _log
        return _log(*args, **kwargs)


log = LogProxy()
