class LazyConsole:
    def __get__(self, instance, owner):
        import sys
        
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
            }
        
        console = Console(force_terminal=True,
                          log_time_format='[%d.%m.%Y][%T]',
                          color_system='truecolor',
                          tab_size=2,
                          file=sys.stderr,
                          theme=Theme({**theme, **{k.upper(): v for k, v in theme.items()}}))
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
