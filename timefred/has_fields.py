from collections import UserList, UserString, UserDict
from typing import Any, TypeVar
import debug

OBJECT_DICT_KEYS = set(object.__dict__)
IGNORED_ATTRS = OBJECT_DICT_KEYS | {'__annotations__',
                                    '__fields__',
                                    '__module__',
                                    '_abc_impl',
                                    '__orig_bases__',
                                    '__abstractmethods__'
                                    }


class BaseHasFields:
    
    def __init__(self, **kwargs) -> None:
        defined_attributes = set(self.__class__.__dict__) - IGNORED_ATTRS
        for name, val in kwargs.items():
            if name in defined_attributes:
                setattr(self, name, val)
                continue
            print(f"{self.__class__.__qualname__}.__init__(...) ignoring keyword argument {name!r}")


class HasFields(dict, BaseHasFields):
    def __setattr__(self, name: str, value) -> None:
        """Makes d.foo = 'bar' also set d['foo']"""
        super().__setattr__(name, value)
        self[name] = value
    
    def __getattr__(self, item):
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


class HasFieldsList(list, BaseHasFields):
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
