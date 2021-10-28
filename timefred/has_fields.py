# import debug
from birdseye import eye




from types import GenericAlias
from typing import TypeVar, Type

K = TypeVar('K')
V = TypeVar('V')
OBJECT_DICT_KEYS = set(object.__dict__)
IGNORED_ATTRS = OBJECT_DICT_KEYS | {'__annotations__',
                                    '__fields__',
                                    '__module__',
                                    '_abc_impl',
                                    '__orig_bases__',
                                    '__abstractmethods__'
                                    }
from cheap_repr import register_repr, ReprHelper, cheap_repr


class BaseHasFields:
    def __init__(self, **kwargs) -> None:
        defined_attributes = set(self.__class__.__dict__) - IGNORED_ATTRS
        for name, val in kwargs.items():
            if name in defined_attributes:
                setattr(self, name, val)
                continue
            print(f"{self.__class__.__qualname__}.__init__(...) ignoring keyword argument {name!r}")

    def __repr__(self):
        return f'{self.__class__.__qualname__} {super().__repr__()}'

class HasFieldsDict(BaseHasFields, dict[K, V]):
    DONT_SET_KEYS = set()
    def __setattr__(self, name: str, value) -> None:
        """Makes d.foo = 'bar' also set d['foo']"""
        super().__setattr__(name, value)
        if name not in self.DONT_SET_KEYS:
            self[name] = value
    
    def __getattr__(self, item):
        """Makes d.foo return d['foo'] AND set d.foo = d['foo']"""
        value = super().__getitem__(item)
        setattr(self, item, value)
        return value
    
    
    
    """def __new__(cls, *args: Any, **kwargs: Any):
        # TODO:
        #  100% Fields | 100% Annotated | Done
        #  100% Fields | Partly Annotated | Done
        #  Partly Fields | 100% Annotated | Done
        #  Partly Fields | Partly Annotated | Done
        #  Non-classvars (i.e init??)
        inst = object.__new__(cls)
        defined_attributes = set(cls.__dict__) - set(cls.__class__.__dict__) - IGNORED_ATTRS
        for name, val in kwargs.items():
            if name in defined_attributes:
                setattr(inst, name, val)
                continue
            inst.__instance_attrs__[name] = val
            print(f"{cls.__qualname__}.__new__(...) ignoring keyword argument {name!r}")
        
        return inst"""
    
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



class HasFieldsDefaultDict(HasFieldsDict[K, V]):
    DONT_SET_KEYS = {'__v_type__'}
    # def __class_getitem__(cls, item: tuple[K, V]) -> GenericAlias:
    #     k_type, v_type = item
    #     cls.__v_type__ = v_type
    #     rv = super().__class_getitem__(item)
    #     return rv
    
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)
    
    def __init__(self, default_factory: Type[V] = None, **kwargs) -> None:
        if default_factory is not None:
            # if self.__v_type__ and self.__v_type__ != default_factory:
            #     from timefred.log import log
            #     log(f'[WARN] self.__v_type__ != default_factory. {self.__v_type__} != {default_factory}')
            self.__v_type__ = default_factory
        
        super().__init__(**kwargs)
    
    # @eye
    def __getitem__(self, k: K) -> V:
        try:
            item = super().__getitem__(k)
        except KeyError as e:
            if self.__v_type__ is None:
                raise ValueError(f"{self.__class__.__qualname__}[{k!r}] raised KeyError, and self.__v_type__ is None")
            constructed = self.__v_type__()
            #print(self.__v_type__, constructed, f'{self.__class__.__qualname__} | After KeyError with {k!r}', with_filename=False, with_fnname=False)
            setattr(self, k, constructed)
            return constructed
        if self.__v_type__ is not None and not isinstance(item, self.__v_type__):
            constructed = self.__v_type__(item)
            #pp(self.__v_type__, item, constructed, title=f'{self.__class__.__qualname__} | No KeyError with {k!r}', with_filename=False, with_fnname=False)
            return constructed
        return item

    def __init_subclass__(cls, *, default_factory: Type[V] = None) -> None:
        super().__init_subclass__()
        if default_factory is not None:
            cls.__v_type__ = default_factory


@register_repr(HasFieldsDefaultDict)
def repr_my_class(has_fields, helper: ReprHelper):
    # helper.level = 1
    return repr(has_fields)
    # return helper.repr_iterable(has_fields.items, f'{has_fields.__class__.__qualname__}{{', '}')

class HasFieldsList(BaseHasFields, list):
    def __init__(self, **kwargs) -> None:
        """Necessary for passed **kwargs to get setattred"""
        BaseHasFields.__init__(self, **kwargs)


class HasFieldsString(str, BaseHasFields):
    def __new__(cls, o, **kwargs):
        """Necessary to prevent **kwargs from passing to str.__new__()"""
        inst = str.__new__(cls, o)
        return inst
    
    def __init__(self, o, **kwargs) -> None:
        BaseHasFields.__init__(self, **kwargs)
