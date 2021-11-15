# import debug
from collections.abc import Iterable
from typing import TypeVar, Type, Generic, Any, Union
from timefred.log import log
import pdbpp

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
    DONT_SET_KEYS = {'DONT_SET_KEYS', '__fields__'}
    def __new__(cls, *args, **kwargs):
        # TypeError: object.__new__(Config) is not safe, use dict.__new__() error
        # inst = object.__new__(cls)
        inst = super().__new__(cls, *args, **kwargs)
        return inst
    
    def __init__(self, **kwargs) -> None:
        """setattr keys (Fields) that are defined on class-level"""
        defined_attributes = set(self.__class__.__dict__) - IGNORED_ATTRS  # todo: return if not kwargs
        for name, val in kwargs.items():
            if name in defined_attributes:
                # this cannot be commented because then tests fail
                setattr(self, name, val)
                continue
            log(f"[WARN] {self.__class__.__qualname__}.__init__(...) ignoring keyword argument {name!r}")
    
    def __repr__(self):
        return f'{self.__class__.__qualname__} {super().__repr__()}'


TYPED_SPACE_K = TypeVar('TYPED_SPACE_K')
TYPED_SPACE_V = TypeVar('TYPED_SPACE_V')
class TypedSpace(Space, Generic[TYPED_SPACE_K, TYPED_SPACE_V]):
    """Sets __v_type__ and casts __getitem__"""
    DONT_SET_KEYS = Space.DONT_SET_KEYS | {'__v_type__'}
    __v_type__: Type[TYPED_SPACE_V]
    
    # Not good because overwrites DefaultDictSpace.__v_type__
    # def __class_getitem__(cls, item: tuple[K, V]) -> GenericAlias:
    #     k_type, v_type = item
    #     cls.__v_type__ = v_type
    #     rv = super().__class_getitem__(item)
    #     return rv
    
    # same logic in __init__ doesn't work
    def __new__(cls, default_factory: Type[TYPED_SPACE_V] = None, **kwargs):
        """Ensures instance has defined __v_type__"""
        inst = super().__new__(cls, **kwargs)
        # inst = Space.__init__(**kwargs)
        if default_factory is None:
            # defined in __init_subclass__()
            assert getattr(cls, '__v_type__', None) is not None
        else:
            # cls.__v_type__ possibly not defined if not __init_subclass__()
            if not hasattr(cls, '__v_type__'):
                assert callable(default_factory)
                inst.__v_type__ = default_factory
        return inst


    def __init_subclass__(cls, *, default_factory: Type[TYPED_SPACE_V] = None) -> None:
        """class Day(DefaultDictSpace, default_factory=Activity)
        class DefaultDictSpace(DefaultSpace[V], DictSpace[K, V])
        """
        super().__init_subclass__()
    
        # Possibly None if defining a generic class like DefaultDictSpace
        if default_factory is not None:
            assert callable(default_factory)
            if hasattr(cls, '__v_type__') and cls.__v_type__ != default_factory:
                raise TypeError(f"Tried to set {cls.__qualname__}.__v_type__ = {default_factory} but it's already defined: {cls.__v_type__}")
            cls.__v_type__ = default_factory
            
    def __getitem__(self, name: TYPED_SPACE_K) -> TYPED_SPACE_V:
        """Ensures self[name] is of __v_type__"""
        # TODO: Space doesn't support __getitem__ or self[name],
        #  so the logic here works only if Foo(TypedSpace, SupportsGetItem)
        try:
            # Should setattr this as well?
            value = super().__getitem__(name)
        except (KeyError, IndexError):
            raise
        else:
            if not isinstance(value, self.__v_type__):
                assert name not in self.__class__.DONT_SET_KEYS | IGNORED_ATTRS, name
                constructed = self.__v_type__(**value)
                # self[name] = constructed # <- bad idea because sets item not attr
                
                # this can be commented out and tests still pass
                setattr(self, name, constructed)
                return constructed
            return value


DEFAULT_SPACE_K = TypeVar('DEFAULT_SPACE_K')
DEFAULT_SPACE_V = TypeVar('DEFAULT_SPACE_V')
class DefaultSpace(TypedSpace[DEFAULT_SPACE_K, DEFAULT_SPACE_V]):
    def __getitem__(self, key: DEFAULT_SPACE_K) -> DEFAULT_SPACE_V:
        """KeyError returns a __v_type__()"""
        try:
            return super().__getitem__(key)
        except KeyError as e:
            # log(f'[debug] {self.__class__.__qualname__}.__getitem__({key!r}) KeyError: {e}')
            constructed = self.__v_type__()
            # self[key] = constructed # <- bad idea because sets item not attr
            
            # this can be commented out and tests still pass
            setattr(self, key, constructed)
            return constructed


DICT_SPACE_K = TypeVar('DICT_SPACE_K')
DICT_SPACE_V = TypeVar('DICT_SPACE_V')

class DictSpace(Space, dict[DICT_SPACE_K, DICT_SPACE_V]):
    def __init__(self, mappable=(), **kwargs) -> None:
        if mappable:
            assert not kwargs
            super().__init__(**dict(mappable))
            return
        assert not mappable, f"{self}({mappable = }, {kwargs = })"
        super().__init__(**kwargs)
    
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
        setattr(self, name, value)
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



DEFAULT_DICT_SPACE_K = TypeVar('DEFAULT_DICT_SPACE_K')
DEFAULT_DICT_SPACE_V = TypeVar('DEFAULT_DICT_SPACE_V')

class DefaultDictSpace(DefaultSpace[DEFAULT_DICT_SPACE_K, DEFAULT_DICT_SPACE_V],
                       DictSpace[DEFAULT_DICT_SPACE_K, DEFAULT_DICT_SPACE_V]):
    # same logic with __init__ doesn't work because
    # TypedSpace.__new__ is called beforehand
    def __new__(cls, default_factory: Type[DEFAULT_DICT_SPACE_V] = None, **kwargs) -> DEFAULT_DICT_SPACE_V:
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
        
        # TypeError: super.__new__(DefaultDictSpace): DefaultDictSpace is not a subtype of super error
        # inst = super(DefaultSpace).__new__(cls, default_factory=default_factory, **kwargs)
        
        # TypeError: super.__new__(): not enough arguments error
        # inst = super(cls).__new__(default_factory=default_factory, **kwargs)
        
        # TypeError: __init__() takes 1 positional argument but 2 were given error
        # inst = DefaultSpace.__new__(cls, default_factory=default_factory, **kwargs)
        
        # TypeError: __new__() missing 1 required positional argument: 'cls' error
        # inst = DefaultSpace.__new__(default_factory=default_factory, **kwargs)

        # TypeError: __new__() missing 1 required positional argument: 'cls' error
        # inst = TypedSpace.__new__(default_factory=default_factory, **kwargs)
        
        # inst = TypedSpace.__new__(cls, default_factory=default_factory, **kwargs)  # good

        # TypeError: __new__() missing 1 required positional argument: 'cls' error
        # inst = super(TypedSpace, cls).__new__(default_factory=default_factory, **kwargs)
        
        # calls Space.__new__() directly, not TypedSpace.__new__(). bad
        # inst = super(TypedSpace, cls).__new__(cls, default_factory=default_factory, **kwargs)

        # calls Space.__new__() directly, not TypedSpace.__new__(). bad
        # inst = super(DictSpace, cls).__new__(cls, default_factory=default_factory, **kwargs)
        
        # TypeError: object.__new__(DefaultDictSpace) is not safe, use dict.__new__() error
        # inst = super(dict, cls).__new__(cls, default_factory=default_factory, **kwargs)

        # calls Space.__new__() directly, not TypedSpace.__new__(). bad
        # inst = DictSpace.__new__(cls, default_factory=default_factory, **kwargs)

        inst = DefaultSpace.__new__(cls, default_factory=default_factory, **kwargs) # good
        
        # Space.__init__(**kwargs) is no good because
        # free keys aren't in defined_attributes, and we still
        # need to setattr class-level fields
        for name, val in kwargs.items():
            assert name not in cls.DONT_SET_KEYS | IGNORED_ATTRS, name
            setattr(inst, name, val)  # also sets keys
        return inst

    # noinspection PyMissingConstructor
    def __init__(self, default_factory: Type[DEFAULT_DICT_SPACE_V] = None, **kwargs):
        # Space.__init__ warns about ignored keyword arguments,
        # which are already setattr'de in __new__, so super().__init__
        # isn't called. Without this overload `default_factory` isn't expected.
        pass




LIST_SPACE_V = TypeVar('LIST_SPACE_V')
class ListSpace(Space, list[LIST_SPACE_V]):
    def __init__(self, iterable: Iterable[LIST_SPACE_V] = (), **kwargs) -> None:
        """Necessary for passed **kwargs to get setattred"""
        list.__init__(self, iterable)
        Space.__init__(self, **kwargs)
        
    

TYPED_LIST_SPACE_V = TypeVar('TYPED_LIST_SPACE_V')
class TypedListSpace(ListSpace[TYPED_LIST_SPACE_V],
                     TypedSpace[Union[int, slice], TYPED_LIST_SPACE_V]):
    def __getitem__(self, name: Union[int, slice]) -> LIST_SPACE_V:
        """Ensures self[name] is of __v_type__"""
        # TODO: Space doesn't support __getitem__ or self[name],
        #  so the logic here works only if Foo(TypedSpace, SupportsGetItem)
        try:
            # Should setattr this as well?
            value = list.__getitem__(self, name)
        except (KeyError, IndexError):
            raise
        else:
            if not isinstance(value, self.__v_type__):
                constructed = self.__v_type__(**value)
                list.__setitem__(self, name, constructed)
                return constructed
            return value

class StringSpace(str, Space): # keep order because repr
    def __new__(cls, o, **kwargs):
        """Necessary to prevent **kwargs from passing to str.__new__()"""
        inst = str.__new__(cls, o)
        return inst
    
    def __init__(self, o, **kwargs) -> None:
        Space.__init__(self, **kwargs)
