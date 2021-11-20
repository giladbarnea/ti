# import debug
from typing import TypeVar, Type, Generic
from collections.abc import Callable
from timefred.log import log
import os

OBJECT_DICT_KEYS = set(object.__dict__)
IGNORED_ATTRS = OBJECT_DICT_KEYS | {
    '__abstractmethods__',
    '__annotations__',
    '__parameters__',
    '__fields__',
    '__getitem__',
    '__module__',
    '__orig_bases__',
    '_abc_impl',
    '_abc_registry',
    '_abc_cache',
    '_abc_negative_cache',
    '_abc_negative_cache_version',
    }


class Space:
    """Does setattr on defined attributes, thus invoking each its Field's __set__ method."""
    DONT_SET_KEYS = {'DONT_SET_KEYS', '__fields__'}
    
    def __new__(cls, *args, **kwargs):
        # TypeError: object.__new__(Config) is not safe, use dict.__new__() error
        # inst = object.__new__(cls)
        instance = super().__new__(cls, *args, **kwargs)
        return instance
    
    def __init__(self, **kwargs) -> None:
        """setattr keys (Fields) that are defined on class-level"""
        defined_attributes = set(self.__class__.__dict__) - IGNORED_ATTRS  # todo: return if not kwargs
        for name, val in kwargs.items():
            if name in defined_attributes:
                # this cannot be commented because then tests fail
                setattr(self, name, val)
                continue
            log.warning(f"{self.__class__.__qualname__}.__init__(...) ignoring keyword argument {name!r}")
    
    def __repr__(self):
        super_repr = super().__repr__()
        if os.getenv('TIMEFRED_REPR', '') == 'short':
            from textwrap import shorten
            super_repr = shorten(super_repr, width=40, placeholder='⟨...⟩')
        return f'{self.__class__.__qualname__} {super_repr}'


TYPED_SPACE_K = TypeVar('TYPED_SPACE_K')
TYPED_SPACE_V = TypeVar('TYPED_SPACE_V')


class TypedSpace(Space, Generic[TYPED_SPACE_K, TYPED_SPACE_V]):
    """Defines __default_factory__, and defines abstract __(get|set|del)item__."""
    DONT_SET_KEYS = Space.DONT_SET_KEYS | {'__default_factory__'}
    __default_factory__: Type[TYPED_SPACE_V]
    
    # Not good because overwrites DefaultAttrDictSpace.__default_factory__
    # def __class_getitem__(cls, item: tuple[K, V]) -> GenericAlias:
    #     k_type, v_type = item
    #     cls.__default_factory__ = v_type
    #     rv = super().__class_getitem__(item)
    #     return rv
    
    # same logic in __init__ doesn't work
    def __new__(cls, default_factory: Type[TYPED_SPACE_V] = None, **kwargs):
        """Ensures instance has defined __default_factory__"""
        instance = super().__new__(cls, **kwargs)
        # inst = Space.__init__(**kwargs)
        if default_factory is None:
            # If we're called e.g TypedDictSpace(), make sure __default_factory__ was defined via TypedDictSpace[Foo]
            assert getattr(cls, '__default_factory__', None) is not None
        else:
            # If we're called e.g. TypedDictSpace(default_factory=Foo),
            # make sure either __default_factory__ was not defined via TypedDictSpace[Bar],
            # or if it was, it's the same as default_factory
            __default_factory__not_defined = not hasattr(cls, '__default_factory__')
            # assert __default_factory__not_defined or cls.__default_factory__ == default_factory, \
            #     f"Tried to set {cls.__qualname__}.__default_factory__ = {default_factory} but it's already defined: {cls.__default_factory__}"
            if __default_factory__not_defined:
                assert callable(default_factory)
                # TODO: this is weird, why not cls.__default_factory__ = default_factory?
                # inst.__default_factory__ = default_factory
                cls.__default_factory__ = default_factory
        return instance
    
    def __init_subclass__(cls, *, default_factory: Type[TYPED_SPACE_V] = None) -> None:
        """class Day(DefaultAttrDictSpace, default_factory=Activity)
        class DefaultAttrDictSpace(DefaultSpace[V], AttrDictSpace[K, V])
        """
        # log.debug(f"TypedDictSpace.__init_subclass__({cls.__qualname__}, {default_factory = })")
        super().__init_subclass__()
        
        # Possibly None if defining a generic class like DefaultAttrDictSpace
        if default_factory is not None:
            assert callable(default_factory)
            if hasattr(cls, '__default_factory__') and cls.__default_factory__ != default_factory:
                raise TypeError(f"Tried to set {cls.__qualname__}.__default_factory__ = {default_factory} but it's already defined: {cls.__default_factory__}")
            cls.__default_factory__ = default_factory
    
    __getitem__: Callable[[TYPED_SPACE_K], TYPED_SPACE_V]

    __setitem__: Callable[[TYPED_SPACE_K, TYPED_SPACE_V], None]
    
    __delitem__: Callable[[TYPED_SPACE_K], None]
