from collections import UserList, UserString
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

class HasFields:
    __instance_attrs__ = dict()
    def __new__(cls, *args: Any, **kwargs: Any):
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
        # for item, annotation in cls.__annotations__.items():
        #     if isinstance(annotation, ForwardRef):
        #         raise NotImplementedError(f"{annotation = }")
        #         evaluated = resolve_forwardref(annotation, cls)
        #         cls.__annotations__[item] = evaluated
        
        return inst
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
    
    # def __repr__(self) -> str:
    #     rv = []
    #     for k in set(self.__class__.__dict__) - IGNORED_ATTRS:
    #         v = getattr(self, k)
    #         rv.append(f'{k}={v}')
    #     return f"{self.__class__.__qualname__}({', '.join(rv)})"
    
    def dict(self, *, exclude=()):
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
        
        return attrs


T = TypeVar('T')


class HasFieldsList(HasFields, UserList[T]): ...


class HasFieldsString(HasFields, UserString): ...
