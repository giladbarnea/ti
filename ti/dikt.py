import typing


class Dikt(dict):
	"""A drop-in replacement for builtin dict, that allows accessing values as attributes (recursively),
	plus added functionality.

	Example::

		>>> document = { 'account_id' : 'foo', 'products' : { 'EndpointSecure' : 'bar' } }
		>>> dokument = Dikt(document)
		>>> dokument.products.EndpointSecure
		bar
		>>> dokument.DOES_NOT_EXIST
		None
		>>> isinstance(dokument, dict)
		True
		>>> # Recusively:
		>>> isinstance(dokument.products, dict)
		True
		>>> # Works as regular dict
		>>> for k, v in dokument.items(): ...

	Class-level attribute annotations implement themselves (act as constructors)::

		>>> class ProductData(Dikt):
		>>>     def validate(self): ...

		>>> class Device(Dikt):
		>>> 	product_data: ProductData

		>>> device = Device({ 'product_data' : ... })
		>>> device.product_data.validate()

	"""

	def __init__(self, mapping=()) -> None:
		super().__init__(mapping)
		self.refresh()

	def refresh(self):
		try:
			annotations = self.__class__.__annotations__
		except AttributeError:
			annotations = {}
		for k, v in self.items():
			if k in annotations and typing.get_origin(annotations[k]) is not typing.Union:
				self.update({k: annotations[k](v)})
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
		return self[item]
