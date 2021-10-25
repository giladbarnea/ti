import inspect
from typing import Any, Callable

from timefred.singleton import Singleton


class UNSET_TYPE(Singleton):
    def __repr__(self):
        return f'UNSET'
    
    def __bool__(self):
        return False


UNSET = UNSET_TYPE()


class Field:
    def __init__(self,
                 default_factory: Callable = UNSET,
                 *,
                 default: Any = UNSET,
                 default_factory_args: tuple = (),
                 caster: Callable = UNSET,
                 optional=False):
        self.default_value = default
        self.default_factory = default_factory
        self.default_factory_args = default_factory_args
        self.caster = caster
        self.cached_value = UNSET
        self.optional = optional
    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f'_{name}'
    
    def _repred_attrs(self) -> dict:
        default_factory_repr = getattr(self.default_factory, '__qualname__', self.default_factory)
        default_factory_args_repr = getattr(self.default_factory_args, '__qualname__', self.default_factory_args)
        caster_repr = getattr(self.caster, '__qualname__', self.caster)
        attrs = dict(default=self.default_value,
                     default_factory=default_factory_repr,
                     default_factory_args=default_factory_args_repr,
                     caster=caster_repr,
                     cached_value=repr(self.cached_value),
                     optional=self.optional)
        return attrs
    
    def __repr__(self):
        return f"{self.__class__.__qualname__}({', '.join([f'{k}={v}' for k, v in self._repred_attrs().items()])})"
    
    def __get__(self, instance, owner):
        if self.cached_value is not UNSET:
            return self.cached_value
        value = getattr(instance, self.private_name, UNSET)
        if value is UNSET:
            if self.default_value is UNSET:
                if self.default_factory is UNSET:
                    if not self.optional:
                        raise AttributeError(f"{owner.__name__}.{self.name} is unset, has no default value nor default_factory")
                else:
                    value = self.default_factory(*self.default_factory_args)
                    # try:
                    #     value = self.default_factory(*self.default_factory_args)
                    # except TypeError as e:
                    #     default_factory_params = inspect.signature(self.default_factory).parameters
                    #     pname = next(iter(default_factory_params))
                    #     if pname == 'self':
                    #         self.default_factory_args = (owner, *self.default_factory_args)
                    #         value = self.default_factory(*self.default_factory_args)
            
            else:
                value = self.default_value
                
        if self.caster and value is not UNSET:
            value = self.caster(value)
        self.cached_value = value
        return value
    
    def __set__(self, instance, value):
        self._unset_cache()
        setattr(instance, self.private_name, value)
    
    def __delete__(self, instance):
        self._unset_cache()
        delattr(instance, self.private_name)
    
    def _unset_cache(self):
        self.cached_value = UNSET
