class LazyConsole:
    def __get__(self, instance, owner):
        import sys
        import os
        from rich.console import Console
        from rich.theme import Theme
        PYCHARM_HOSTED = os.getenv('PYCHARM_HOSTED')
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
        console = Console(
                # force_terminal=True,
                # log_time_format='[%d.%m.%Y][%T]',
                # safe_box=False,
                # soft_wrap=True,
                log_time=False,
                color_system='auto' if PYCHARM_HOSTED else 'truecolor',
                tab_size=2,
                log_path=True,
                file=sys.stdout if PYCHARM_HOSTED else sys.stderr,
                theme=Theme({**theme, **{k.upper(): v for k, v in theme.items()}}))
        if console.width == 80:
            console.width = 160
        console.log(f'[debug]{console.width = }')
        return console


class LogProxy:
    console = LazyConsole()
    _log = None
    
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('_stack_offset', 2)
        if self._log:
            return self._log(*args, **kwargs)
        _log = self.console.log
        self._log = _log
        return _log(*args, **kwargs)
    
    @staticmethod
    def _prepend_level(level: str, *msg_args) -> tuple[str]:
        return tuple(f'[{level}] {arg}' for arg in msg_args)
    
    def debug(self, *args, **kwargs):
        return self.__call__('\n\t'.join(self._prepend_level('debug', *args)), **kwargs, _stack_offset=3)
    
    def warning(self, *args, **kwargs):
        return self.__call__(*self._prepend_level('warning', *args), **kwargs, _stack_offset=3)
    
    def error(self, *args, **kwargs):
        return self.__call__(*self._prepend_level('error', *args), **kwargs, _stack_offset=3)
    
    def fatal(self, *args, **kwargs):
        return self.__call__(*self._prepend_level('fatal', *args), **kwargs, _stack_offset=3)
    
    def success(self, *args, **kwargs):
        return self.__call__(*self._prepend_level('success', *args), **kwargs, _stack_offset=3)
    
    def prompt(self, *args, **kwargs):
        return self.__call__(*self._prepend_level('prompt', *args), **kwargs, _stack_offset=3)
    
    def title(self, *args, **kwargs):
        return self.__call__(*self._prepend_level('title', *args), **kwargs, _stack_offset=3)


log = LogProxy()