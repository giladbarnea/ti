import re

def task(s):
	return f'[b rgb(58,150,221)]{s}[/b rgb(58,150,221)]'

def tagC(s):
	return f'[rgb(204,120,50)]{s}[/rgb(204,120,50)]'

def red(s):
	return f'[red]{s}[/red]'

def green(s):
	return f'[green]{s}[/green]'

def yellow(s):
	return f'[yellow]{s}[/yellow]'

def blue(s):
	return f'[blue]{s}[/blue]'


color_regex = re.compile("(\x9B|\x1B\\[)[0-?]*[ -/]*[@-~]")


def strip_color(s):
	"""Strip color from string."""
	return color_regex.sub("", s)


def len_color(s):
	"""Compute how long the color escape sequences in the string are."""
	return len(s) - len(strip_color(s))


def ljust_with_color(s, n):
	"""ljust string that might contain color."""
	return s.ljust(n + len_color(s))
