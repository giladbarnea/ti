import re
from colorama import Fore
def red(s):
	return Fore.RED + s + Fore.RESET


def green(s):
	return Fore.GREEN + s + Fore.RESET


def yellow(s):
	return Fore.YELLOW + s + Fore.RESET


def blue(s):
	return Fore.BLUE + s + Fore.RESET


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