from timefred import color as c


def confirm(question):
	return input(f' {c.blue("?")} ' + question + c.b(' [yn]  ')).lower() in ('y', 'yes')



from time import perf_counter_ns


def timeit(function):
	def decorator(*args, **kwargs):
		a = perf_counter_ns()
		try:
			rv = function(*args, **kwargs)
			return rv
		finally:
			b = perf_counter_ns()
			print(f'{function.__qualname__}({", ".join(args) + ", " if args else ""}{", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())}) took {round((b - a) / 1000, 2):,} μs ({round((b - a) / 1_000_000, 1):,} ms)')

	return decorator

