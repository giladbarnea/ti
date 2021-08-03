"""
exec(compile(Path('~/prebreak.py').open().read(), '~/prebreak.py', 'exec'))
# OR:
import os; from pathlib import Path; exec(compile(Path(prebreak := os.getenv("PYTHONPREBREAK", Path(os.getenv("HOME")) / 'prebreak.py')).open().read(), prebreak, 'exec'))
# OR: (for python < 3.8)
prebreak = os.getenv("PYTHONPREBREAK", os.path.join(os.getenv("HOME"), 'prebreak.py'))
exec(compile(Path(prebreak).open().read(), prebreak, 'exec'))
# OR:
# %run '/home/gilad/prebreak.py'

# PREBREAK_FORCE_INSTALL, PREBREAK_SHOW_ADDONS, PREBREAK_RICH_TB, PREBREAK_PATCH_PRINT, PREBREAK_PATCH_LOGGING
"""

import sys

try:
	builtins = __import__("__builtin__")
except ImportError:
	builtins = __import__("builtins")
import os

try:
	import rich
except ModuleNotFoundError:
	if os.getenv('PREBREAK_FORCE_INSTALL'):
		import json

		__install = json.loads(os.getenv('PREBREAK_FORCE_INSTALL'))
		pkgs = " ".join(pkg for pkg in __install.keys() if __install[pkg])
		os.system(f'pip install {pkgs}')
	raise
import inspect
from rich.console import Console

try:
	from IPython import start_ipython as startipy, get_ipython as getipy
except ModuleNotFoundError:
	pass
else:
	builtins.startipy = startipy
	builtins.getipy = getipy
try:
	from icecream import ic
except ModuleNotFoundError:
	pass
else:
	builtins.ic = ic
try:
	from loguru import logger

	logger = logger.opt(colors=True)
except ModuleNotFoundError:
	pass
else:
	builtins.logger = logger
from pathlib import Path

here = Path('.').absolute()


# TODO: instead of patching builtins, get namespace (print this file's locals when called from IPython etc)
def __build_getprops_getmeths():
	from typing import Union, Tuple, List, NoReturn
	try:
		from typing import Literal
		Constraint = Literal['regular', 'private', 'dunder']
	except ImportError:
		from typing import NamedTuple
		Constraint = NamedTuple('Constraint', [('regular', str), ('private', str), ('dunder', str)])

	def __set_constraints(only: Union[Constraint, Tuple[Constraint]]):
		"""If `only` is None, this means no constraints: `regular = private = dunder = True` (show all).
		If it's a string (e.g. 'regular'), switch on `regular = True`, and switch off others (show only regular props).
		If it's a tuple (e.g. `('regular', 'private')`), switch on `regular = True, private = True` (don't show dunder)."""

		def __set_constraint(_constraint: Constraint, _regular: bool, _private: bool, _dunder: bool) -> Tuple[bool, bool, bool]:
			if _constraint == 'regular':
				_regular = True
			elif _constraint == 'private':
				_private = True
			elif _constraint == 'dunder':
				_dunder = True
			else:
				con.log("[WARN] 'only' arg is can be only (an iterable composed of) 'regular', 'private' or 'dunder'. returning as-is")
			return _regular, _private, _dunder

		if only is not None:
			regular = private = dunder = False
			if isinstance(only, str):
				regular, private, dunder = __set_constraint(only, regular, private, dunder)
			else:  # iterable
				for constraint in only:
					regular, private, dunder = __set_constraint(constraint, regular, private, dunder)
		else:
			regular = private = dunder = True
		return regular, private, dunder

	def __ismeth(value) -> bool:
		string = str(type(value))
		return 'method' in string or 'wrapper' in string or 'function' in string

	def __should_skip(prop, regular: bool, private: bool, dunder: bool, *, include, exclude) -> bool:
		if prop in exclude:
			return True
		if include and prop not in include:
			return True
		if prop.startswith('__'):
			if not dunder:
				return True
		elif prop.startswith('_'):
			if not private:
				return True
		elif not regular:
			return True
		return False

	def _getprops(obj,
				  values: bool = False,
				  only: Union[Constraint, Tuple[Constraint]] = None,
				  exclude: Union[str, Tuple] = (),
				  include: Union[str, Tuple] = ()
				  ):
		"""
		:param values: Specify True to check and return property values
		:param only: Either 'regular', 'private', 'dunder' or a tuple containing any of them
		:param exclude: A str or a tuple of strings specifying which props to ignore.
		:param include: A str or a tuple of strings specifying which props to include. All others are ignored.
		`exclude` and `include` are mutually exclusive.
		"""
		# TODO: compare rv with inspect.getmembers()
		if include and exclude:
			con.log(f"[WARN] _getprops({repr(obj)}) | can't have both include and exclude")
			return
		if include:
			# ensure include is a tuple
			if isinstance(include, str):
				include = (include,)
		if exclude:
			# ensure exclude is a tuple
			if isinstance(exclude, str):
				exclude = (exclude,)
		try:
			proplist = obj.__dir__()
		except:
			proplist = dir(obj)
		props = []
		regular, private, dunder = __set_constraints(only)
		__obj_props = ('__class__', '__doc__')
		for prop in proplist:
			if __should_skip(prop, regular, private, dunder, include=include, exclude=(*exclude, *__obj_props), ):
				continue
			try:
				value = getattr(obj, prop)
			except Exception as e:
				con.log(f'{e.__class__.__qualname__} when trying to get attr: "{prop}": {", ".join(map(repr, e.args))}. skipping.')
				continue
			if __ismeth(value):
				continue
			if values:
				props.append({prop: value})
			else:
				props.append(prop)
		if values:
			sort = lambda x: next(iter(x))
		else:
			sort = None
		return sorted(props, key=sort)

	def _getmeths(obj,
				  sigs: bool = False,
				  only: Union[Constraint, Tuple[Constraint]] = None,
				  exclude: Union[str, Tuple] = (),
				  include: Union[str, Tuple] = ()) -> List[str]:
		"""
		:param sigs: Specify True to check and return method signatures
		:param only: Either 'regular', 'private', 'dunder' or a tuple containing any of them
		:param exclude: A str or a tuple of strings specifying which props to ignore.
		:param include: A str or a tuple of strings specifying which props to include. All others are ignored.
		`exclude` and `include` are mutually exclusive.
		"""
		if include and exclude:
			con.log(f"[WARN] _getprops({repr(obj)}) | can't have both include and exclude")
			return []
		if include:
			# ensure include is a tuple
			if isinstance(include, str):
				include = (include,)
		if exclude:
			# ensure exclude is a tuple
			if isinstance(exclude, str):
				exclude = (exclude,)
		try:
			proplist = obj.__dir__()
		except:
			proplist = dir(obj)
		regular, private, dunder = __set_constraints(only)
		meths = []
		__obj_meths = ('__delattr__',
					   '__dir__',
					   '__eq__',
					   '__format__',
					   '__ge__',
					   '__getattribute__',
					   '__gt__',
					   '__hash__',
					   '__init__',
					   '__init_subclass__',
					   '__le__',
					   '__lt__',
					   '__ne__',
					   '__new__',
					   '__reduce__',
					   '__reduce_ex__',
					   '__repr__',
					   '__setattr__',
					   '__sizeof__',
					   '__str__',
					   '__subclasshook__')
		for prop in proplist:
			if __should_skip(prop, regular, private, dunder, include=include, exclude=(*exclude, *__obj_meths), ):
				continue
			try:
				meth = getattr(obj, prop)
			except Exception as e:
				con.log(f'[_getmeths({obj})] {e.__class__.__qualname__} when trying to get attr: "{prop}": {", ".join(map(repr, e.args))}. skipping.')
				continue
			if not __ismeth(meth):
				continue
			if sigs:
				try:
					sig: inspect.Signature = inspect.signature(meth)
					meths.append({f'{prop}()': dict(sig.parameters.items())})
				except ValueError as e:
					con.log(f'[_getmeths({obj})] ValueError: {", ".join(map(repr, e.args))}. appending meth without args')
					meths.append(prop)
			else:
				meths.append(prop)
		if sigs:
			sort = lambda x: next(iter(x))
		else:
			sort = None
		return sorted(meths, key=sort)

	def _inspectfn(fn: callable) -> NoReturn:
		"""Calls all relevant functions from `inspect` module on `fn` and prints the results.
		Doesn't return anything."""
		for inspectmethname in filter(lambda m: str(m) not in ('getsource', 'getsourcelines', 'findsource', 'getmembers'),
									  _getmeths(inspect)):
			if inspectmethname.startswith('is'):
				continue
			try:
				inspectmeth = getattr(inspect, inspectmethname)
				rv = inspectmeth(fn)
				con.print(f'\n[b bright_white]{inspectmeth.__name__}({fn.__name__})[/] → {type(rv).__qualname__}:', end='\n    ')
				con.print(rv, end='\n')
			except:
				pass

	return _getprops, _getmeths, _inspectfn


getprops, getmeths, inspectfn = __build_getprops_getmeths()
con = Console(log_time_format='[%d.%m.%Y][%T]')


# from rich.pretty import install
# install(console=con,indent_guides=True,expand_all=True)
# if print.__module__ == 'builtins':  # unpatched
#     this is not a good idea because \033[... aren't parsed
#     import builtins
#     from rich import print
#     builtins.print = print
# if sys.exc_info()[0]:
#     exctype, excinst, tb = sys.exc_info()
#     if not isinstance(excinst, (SystemExit, SyntaxError)):
#         con.log(f'prebreak: building fancy trace... (sys.exc_info() = {sys.exc_info()})')
#         con.print_exception(show_locals=True, extra_lines=10)
def mm(topic, subtopic=None):
	mm_args = f'{topic}'
	if subtopic:
		mm_args += f' {subtopic}'
	import subprocess as sp
	sp.check_call(f'"$(where python3.8 | tail -1)" -m manuals {mm_args}', shell=True, executable='/bin/zsh')


# os.system(f'zsh -c "$(where python3.8 | tail -1) -m manuals {mm_args}"')


def _get_var_names(arg_idx=0, offset_or_frameinfo = 2) -> str:
	try:
		if not offset_or_frameinfo or isinstance(offset_or_frameinfo, int):
			currframe = inspect.currentframe()
			outer = inspect.getouterframes(currframe)
			frameinfo = outer[offset_or_frameinfo]
		else:
			frameinfo = offset_or_frameinfo
		ctx = frameinfo.code_context[0].strip()
		argnames = ctx[ctx.find('(') + 1:-1].split(', ')
		if arg_idx is None:
			varnames = ', '.join(map(str.strip, argnames))
		else:
			# varnames = ', '.join(map(str.strip, argnames[count - 1]))
			varnames = f'{frameinfo.filename.split("/")[-1]} | {frameinfo.function}() | {argnames[arg_idx].strip()}'
		return varnames
	except Exception as e:
		con.log(e.__class__, e)
		return ""


def _get_caller_frame_info(offset=2) -> inspect.FrameInfo:
	currframe = inspect.currentframe()
	outer = inspect.getouterframes(currframe)
	frameinfo = outer[offset]
	return frameinfo


def what(obj, **kwargs):
	"""rich.inspect(methods=True)"""
	rich.inspect(obj, methods=True, title=_get_var_names(), **kwargs)


def ww(obj, **kwargs):
	"""rich.inspect(methods=True, help=True)"""
	rich.inspect(obj, methods=True, help=True, title=_get_var_names(), **kwargs)


def www(obj, **kwargs):
	"""rich.inspect(methods=True, help=True, private=True)"""
	rich.inspect(obj, methods=True, help=True, private=True, title=_get_var_names(), **kwargs)


def wwww(obj, **kwargs):
	"""rich.inspect(all=True)"""
	rich.inspect(obj, all=True, title=_get_var_names(), **kwargs)


def who():
	con.log('locals:', log_locals=True, _stack_offset=2)


builtins_before = set(builtins.__dict__.keys())
builtins.sys = sys
builtins.rich = rich
builtins._get_var_names = _get_var_names
builtins.getprops = getprops
builtins.getmeths = getmeths
builtins.inspectfn = inspectfn
builtins.mm = mm
builtins.what = what
builtins.ww = ww
builtins.www = www
builtins.wwww = wwww
builtins.who = who
builtins.pr = rich.print
builtins.con = con
if os.getenv('PREBREAK_SHOW_ADDONS') or any(arg == '--show-addons' for arg in sys.argv[1:]):
	from contextlib import suppress

	with suppress(NameError):
		# Sometimes happen with pdbpp breakpoint, not sure why
		builtins_diff = {k: v for k, v in builtins.__dict__.items() if k not in builtins_before}
		con.log(f'[b]addons:[/]')
		for addon_name, addon in builtins_diff.items():
			con.log(f'\t{addon_name}[dim]: {type(addon)}[/]')

if os.getenv('PREBREAK_RICH_TB') or any(arg == '--rich-tb' for arg in sys.argv[1:]):
	from rich.traceback import install

	install(extra_lines=5, show_locals=True)

if os.getenv('PREBREAK_PATCH_PRINT', '').lower() in ('1', 'true') or any(arg == '--patch-print' for arg in sys.argv[1:]):
	from rich.pretty import pretty_repr

	builtins.pretty_repr = pretty_repr

	def __print_patch(*args, **kwargs):
		formatted_args = []
		caller_frameinfo = _get_caller_frame_info(offset=2)
		for i, arg in enumerate(args):
			# if repr(arg).startswith('"') or repr(arg).startswith("'"):
			# 	formatted_args.append(f'[bright_white]{caller_frameinfo.filename} | {caller_frameinfo.function}() |[/] [dim italic]{type(arg)}[/]')
			# else:
			# 	formatted_args.append(f'[bright_white]{_get_var_names(i, offset_or_frameinfo=caller_frameinfo)}:[/] [dim italic]{type(arg)}[/]')
			formatted_args.append(f'[bright_white]{_get_var_names(i, offset_or_frameinfo=caller_frameinfo)}:[/] [dim italic]{type(arg)}[/]')
			pretty = pretty_repr(arg, max_width=160, expand_all=True)
			# try:
			# except RecursionError:
			# 	from pprint import pformat
			# 	pretty = pformat(arg, indent=4, width=160, sort_dicts=True)

			formatted_args.append(pretty + '\n')
		rich.print(*formatted_args, **kwargs)


	from copy import deepcopy

	# Todo: verify if patched
	builtins.__print__ = deepcopy(print)
	builtins.print = __print_patch

if os.getenv('PREBREAK_PATCH_LOGGING') or any(arg == '--patch-logging' for arg in sys.argv[1:]):
	import logging

	try:
		import loguru
	except ModuleNotFoundError:
		pass
	else:
		loggercls = logging.getLoggerClass()
		loggercls.debug = loguru.logger.debug
		loggercls.info = loguru.logger.info
		loggercls.warning = loguru.logger.warning
		loggercls.error = loguru.logger.error
		loggercls.exception = loguru.logger.exception
