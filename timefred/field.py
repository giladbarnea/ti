from typing import Any, Callable

# from pdbpp import break_on_exc

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
                 cast: Callable = UNSET,
                 optional=False,
                 cache=False
                 ):
        self.default = default
        self.default_factory = default_factory
        # self.default_factory_args = default_factory_args
        self.caster = cast
        self.should_cache = cache
        self.cached_value = UNSET
        
        self.optional = optional
    
    def __set_name__(self, owner, name):
        self.name = name
        # self.private_name = f'_{name}'
        

    def __call__(self, method):
        """Allows for using Field as a decorator with args, e.g `Field(optional=True)`"""
        if not callable(method):
            raise TypeError(f"A Field instance was called. This can happen only as a method decorator")
        self.default_factory = method
        return self
    
    def _repred_attrs(self) -> dict:
        default_factory_repr = getattr(self.default_factory, '__qualname__', self.default_factory)
        caster_repr = getattr(self.caster, '__qualname__', self.caster)
        attrs = dict(default=self.default,
                     default_factory=default_factory_repr,
                     cast=caster_repr,
                     cached_value=repr(self.cached_value),
                     optional=self.optional,
                     cache=self.should_cache)
        return attrs
    
    def __repr__(self):
        return f"{self.__class__.__qualname__}⟨{self.name!r}⟩({', '.join([f'{k}={v}' for k, v in self._repred_attrs().items()])})"
    
    def __get__(self, instance, owner):
        if self.should_cache and self.cached_value is not UNSET:
            return self.cached_value
        if hasattr(instance, '__fields__'):
            value = instance.__fields__.get(self.name, UNSET)
        else:
            setattr(instance, '__fields__', {self.name: UNSET})
            value = UNSET
        
            
        if value is UNSET:
            if self.default is UNSET:
                if self.default_factory is UNSET:
                    if not self.optional:
                        raise AttributeError(f"{owner.__name__}.{self.name} is unset, has no default value nor default_factory")
                else:
                    value = self.default_factory()
            else:
                value = self.default
                
        if self.caster and value is not UNSET:
            value = self.caster(value)
        
        if self.should_cache:
            self.cached_value = value
        return value
    
    def __set__(self, instance, value):
        self._unset_cache()
        if hasattr(instance, '__fields__'):
            instance.__fields__[self.name] = value
        else:
            setattr(instance, '__fields__', {self.name: value})
    
    def __delete__(self, instance):
        self._unset_cache()
        if hasattr(instance, '__fields__'):
            del instance.__fields__[self.name]
        else:
            setattr(instance, '__fields__', {})
    
    def _unset_cache(self):
        if self.should_cache:
            self.cached_value = UNSET
