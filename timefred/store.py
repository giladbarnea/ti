from os import path, getenv

import yaml


# @dataclass
# from timefred.util import timeit


class Data(dict):
	# doesn't write well to .timefred-sheet
	pass
	# work: List[Item]
	# interrupt_stack: List


class Store:

	def __init__(self, filename):
		self.filename = filename

	def load(self): # perf: 150ms
		if path.exists(self.filename):
			with open(self.filename) as f:
				data = yaml.load(f, Loader=yaml.FullLoader)
				if 'work' not in data:
					data['work'] = []
				if 'interrupt_stack' not in data:
					data['interrupt_stack'] = []

		else:
			data = {'work': [], 'interrupt_stack': []}
		return data

	def dump(self, data):
		if getenv('TF_DRYRUN', "").lower() in ('1', 'true'):
			print('\n\tDRY RUN, NOT DUMPING\n')
			return False
		with open(self.filename, 'w') as f:
			# json.dump(data, f, separators=(',', ': '), indent=2)
			yaml.dump(data, f, indent=4)
			return True



from timefred.config import config
store = Store(path.expanduser(config.sheet.path))
