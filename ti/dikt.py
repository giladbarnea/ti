import typing

def extract_origin(t):
	"""Extract e.g `dict` from `Optional[dict]`.
	Returns None if non-extractable."""
	origin = typing.get_origin(t)
	if origin is None: # Any
		return None
	if origin is not typing.Union:
		return origin

	# origin is Union
	origins = [a for a in typing.get_args(origin) if a != type(None)]
	if len(origins) == 1:
		return origins[0]
	return None

class Dikt(dict):
	def __init__(self, mapping=()) -> None:
		super().__init__(mapping)
		self.refresh()

	def update_by_annotation(self, k, v) -> bool:
		try:
			annotations = self.__class__.__annotations__
		except AttributeError:
			return False

		if k not in annotations:
			return False

		origin = extract_origin(annotations[k])
		if not origin:
			return False

		try:
			constructed_val = annotations[k](v)
		except:
			return False

		self.update({k: constructed_val})
		return True

	def refresh(self):
		for k, v in self.items():
			if self.update_by_annotation(k, v):
					continue

			if isinstance(v, dict):
				self.update({k: Dikt(v)})
			else:
				self.update({k: v})

	def __repr__(self) -> str:
		name = self.__class__.__qualname__
		if not self:
			return f"{name}({{}})"
		rv = f"{name}({{\n    "
		max_key_len = max(map(len, self.keys()))
		for k, v in self.items():
			# if k.startswith('_'):
			# 	continue
			rv += f"{str(k).ljust(max_key_len, ' ')} : {repr(v).replace('    ', '        ')},\n    "
		rv += "})"
		return rv

	# def __getitem__(self, k):
	#     """Like `normal_dict.get('foo', None)`"""
	#     try:
	#         return super().__getitem__(k)
	#     except KeyError as e:
	#         return None

	def __getattr__(self, item):
		"""Makes `d.foo` call `d['foo']`"""
		return self[item]


	def __setattr__(self, name: str, value) -> None:
		super().__setattr__(name, value)
		self[name] = value