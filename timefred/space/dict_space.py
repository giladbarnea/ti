"""
2 inheritance branches:

                Space
                 |
          DictSpace(dict) (__getitem__, __setitem__)
                |                                  \
TypedDictSpace (__default_factory__)             AttrDictSpace (__getattr__, __setattr__)
                \                                  /
DefaultDictSpace (KeyError __default_factory__)           /
                  \                            /
                        DefaultAttrDictSpace
        
"""
from typing import TypeVar, Type

from timefred.space import Space, TypedSpace
from .space import IGNORED_ATTRS
from timefred.log import log
# from pdbpp import break_on_exc
DICT_SPACE_K = TypeVar('DICT_SPACE_K')
DICT_SPACE_V = TypeVar('DICT_SPACE_V')

class DictSpace(Space, dict[DICT_SPACE_K, DICT_SPACE_V]):
    """Inherits from dict thus defining __getitem__, __setitem__ etc,
    and inherits from Space thus `setattr`s defined fields in __init__."""
    
    # @break_on_exc
    def __new__(cls, *args, **kwargs) -> "DictSpace":
        # if mappable:
        #     assert not kwargs, f"{cls}.__new__({mappable = }, {kwargs = })"
        #     instance = dict.__new__(cls, **dict(mappable))
        #     return instance
        if args:
            assert not kwargs, f"{cls}.__new__({args = }, {kwargs = })"
            instance = dict.__new__(cls, **dict(*args))
            return instance
        # assert not mappable, f"{cls}.__new__({mappable = }, {kwargs = })"
        assert not args, f"{cls}.__new__({args = }, {kwargs = })"
        instance = dict.__new__(cls, **kwargs)
        return instance


TYPED_DICT_SPACE_K = TypeVar('TYPED_DICT_SPACE_K')
TYPED_DICT_SPACE_V = TypeVar('TYPED_DICT_SPACE_V')


class TypedDictSpace(TypedSpace[TYPED_DICT_SPACE_K, TYPED_DICT_SPACE_V],
                     DictSpace[TYPED_DICT_SPACE_K, TYPED_DICT_SPACE_V]):
# class TypedDictSpace(TypedSpace):
    """Casts __getitem__, No KeyError handling. Inherits from TypedSpace thus defining __default_factory__."""
    __default_factory__: Type[TYPED_DICT_SPACE_V]
    
    
    # def __getitem__(self, name: TYPED_DICT_SPACE_K) -> TYPED_DICT_SPACE_V:
    def __getitem__(self, name):
        """Ensures self[name] is of __default_factory__"""
        try:
            # Should setattr this as well?
            value = super().__getitem__(name)
        except (KeyError, IndexError):
            raise
        else:
            if not isinstance(value, self.__default_factory__):
                assert name not in self.__class__.DONT_SET_KEYS | IGNORED_ATTRS, \
                    (f"{self.__class__.__qualname__}.__getitem__({name!r}) returned {value!r} but it's not of type {self.__default_factory__.__qualname__}"
                     f"and it's in {self.__class__.DONT_SET_KEYS | IGNORED_ATTRS = }")
                constructed = self.__default_factory__(**value)
                # self[name] = constructed # <- bad idea because sets item not attr
                # this cannot be commented out, tests fail
                setattr(self, name, constructed)
                return constructed
            return value


    def values(self) -> list[TYPED_DICT_SPACE_V]:
        values: list[TYPED_DICT_SPACE_V] = []
        for key in self.keys():
            value = self[key]
            values.append(value)
        return values
    

DEFAULT_DICT_SPACE_K = TypeVar('DEFAULT_DICT_SPACE_K')
DEFAULT_DICT_SPACE_V = TypeVar('DEFAULT_DICT_SPACE_V')


class DefaultDictSpace(TypedDictSpace[DEFAULT_DICT_SPACE_K, DEFAULT_DICT_SPACE_V]):
    """KeyError returns a __default_factory__() (also casts __getitem__ via TypedDictSpace)"""
    
    # def __getitem__(self, key: DEFAULT_SPACE_K) -> DEFAULT_SPACE_V:
    def __getitem__(self, name):
        try:
            value = super().__getitem__(name)
            # print(value)
            return value
        except KeyError as e:
            # log(f'[debug] {self.__class__.__qualname__}.__getitem__({name!r}) KeyError: {e}')
            constructed = self.__default_factory__()
            # self[name] = constructed # <- bad idea because sets item not attr
            
            # this cannot be commented out, tests fail
            setattr(self, name, constructed)
            return constructed


ATTR_DICT_SPACE_K = TypeVar('ATTR_DICT_SPACE_K')
ATTR_DICT_SPACE_V = TypeVar('ATTR_DICT_SPACE_V')
class AttrDictSpace(DictSpace[ATTR_DICT_SPACE_K, ATTR_DICT_SPACE_V]):
    """Implements __getattr__ and __setattr__ (gets / sets keys),
    and inherits from `DictSpace(dict)`, thus defining __getitem__ and __setitem__.
    No __default_factory__ or default stuff."""
    
    def __setattr__(self, name: str, value) -> None:
        """Setting d.foo also sets d['foo']"""
        super().__setattr__(name, value)
        if name not in self.__class__.DONT_SET_KEYS:
            self[name] = value
    
    def __getattr__(self, name: str):
        """d.foo returns d['foo'] AND sets d.foo = d['foo']"""
        try:
            value = super().__getitem__(name)
        except KeyError as keyerr:
            value = super().__getattribute__(name)
            breakpoint()
        
        # this can be commented out and tests still pass
        # setattr(self, name, value)
        return value
    
    # def __iter__(self):
    #     return iter(set(self.__class__.__dict__) - IGNORED_ATTRS)
    
    # def __repr__(self) -> str:
    #     rv = []
    #     for k in set(self.__class__.__dict__) - IGNORED_ATTRS:
    #         v = getattr(self, k)
    #         rv.append(f'{k}={v}')
    #     return f"{self.__class__.__qualname__}({', '.join(rv)})"
    
    """def dict(self, *, exclude=()):
        if not isinstance(exclude, tuple):
            exclude = (exclude,)
        attrs = {}
        for k in self.__annotations__:
            if k in exclude:
                continue
            v = getattr(self, k)
            if v:
                # with suppress(AttributeError):
                #     attrs[k] = v.HHmmss
                #     continue
                #
                # with suppress(AttributeError):
                #     attrs[k] = v.dict()
                #     continue
                
                attrs[k] = v
        
        return attrs"""


DEFAULT_ATTR_DICT_SPACE_K = TypeVar('DEFAULT_ATTR_DICT_SPACE_K')
DEFAULT_ATTR_DICT_SPACE_V = TypeVar('DEFAULT_ATTR_DICT_SPACE_V')


class DefaultAttrDictSpace(DefaultDictSpace[DEFAULT_ATTR_DICT_SPACE_K, DEFAULT_ATTR_DICT_SPACE_V],
                           AttrDictSpace[DEFAULT_ATTR_DICT_SPACE_K, DEFAULT_ATTR_DICT_SPACE_V]):

    """Casts / returns __default_factory__(...) via DefaultDictSpace,
    and __getattr__ and __setattr__ via AttrDictSpace."""
    
    # same logic with __init__ doesn't work because
    # TypedDictSpace.__new__ is called beforehand
    def __new__(cls, default_factory: Type[DEFAULT_ATTR_DICT_SPACE_V] = None, **kwargs) -> DEFAULT_ATTR_DICT_SPACE_V:
        # log(f'[title]{cls.__qualname__}.__new__({default_factory=!r}, {kwargs=!r})...')
        # TypeError: __init__() takes 1 positional argument but 2 were given error
        # inst = super().__new__(cls, default_factory=default_factory, **kwargs)
        
        # TypeError: __new__() missing 1 required positional argument: 'cls' error
        # inst = super().__new__(default_factory=default_factory, **kwargs)
        
        # TypeError: __new__() missing 1 required positional argument: 'cls' error
        # inst = super(DefaultSpace, cls).__new__(default_factory=default_factory, **kwargs)
        
        # TypeError: __init__() takes 1 positional argument but 2 were given error
        # inst = super(DefaultSpace, cls).__new__(cls, default_factory=default_factory, **kwargs)
        
        # TypeError: super.__new__(): not enough arguments error
        # inst = super(DefaultSpace).__new__(default_factory=default_factory, **kwargs)
        
        # TypeError: super.__new__(DefaultAttrDictSpace): DefaultAttrDictSpace is not a subtype of super error
        # inst = super(DefaultSpace).__new__(cls, default_factory=default_factory, **kwargs)
        
        # TypeError: super.__new__(): not enough arguments error
        # inst = super(cls).__new__(default_factory=default_factory, **kwargs)
        
        # TypeError: __init__() takes 1 positional argument but 2 were given error
        # inst = DefaultSpace.__new__(cls, default_factory=default_factory, **kwargs)
        
        # TypeError: __new__() missing 1 required positional argument: 'cls' error
        # inst = DefaultSpace.__new__(default_factory=default_factory, **kwargs)
        
        # TypeError: __new__() missing 1 required positional argument: 'cls' error
        # inst = TypedDictSpace.__new__(default_factory=default_factory, **kwargs)
        
        # inst = TypedDictSpace.__new__(cls, default_factory=default_factory, **kwargs)  # good
        
        # TypeError: __new__() missing 1 required positional argument: 'cls' error
        # inst = super(TypedDictSpace, cls).__new__(default_factory=default_factory, **kwargs)
        
        # calls Space.__new__() directly, not TypedDictSpace.__new__(). bad
        # inst = super(TypedDictSpace, cls).__new__(cls, default_factory=default_factory, **kwargs)
        
        # calls Space.__new__() directly, not TypedDictSpace.__new__(). bad
        # inst = super(AttrDictSpace, cls).__new__(cls, default_factory=default_factory, **kwargs)
        
        # TypeError: object.__new__(DefaultAttrDictSpace) is not safe, use dict.__new__() error
        # inst = super(dict, cls).__new__(cls, default_factory=default_factory, **kwargs)
        
        # calls Space.__new__() directly, not TypedDictSpace.__new__(). bad
        # inst = AttrDictSpace.__new__(cls, default_factory=default_factory, **kwargs)
        
        instance = DefaultDictSpace.__new__(cls, default_factory=default_factory, **kwargs)  # good
        
        # Space.__init__(**kwargs) is no good because
        # free keys aren't in defined_attributes, and we still
        # need to setattr class-level fields
        for name, val in kwargs.items():
            assert name not in cls.DONT_SET_KEYS | IGNORED_ATTRS, f"{name=!r} in {cls.DONT_SET_KEYS | IGNORED_ATTRS=!r}"
            setattr(instance, name, val)  # also sets keys
        return instance
    
    # noinspection PyMissingConstructor
    def __init__(self, default_factory: Type[DEFAULT_ATTR_DICT_SPACE_V] = None, **kwargs):
        # Space.__init__ warns about ignored keyword arguments,
        # which are already setattr'de in __new__, so super().__init__
        # isn't called. Without this overload `default_factory` isn't expected.
        pass
    # def __getitem__(self, key: DEFAULT_DICT_SPACE_K) -> DEFAULT_DICT_SPACE_V: ...
