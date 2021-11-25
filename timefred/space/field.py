from collections.abc import Mapping
from typing import Any, Callable, Type, TypeVar, Protocol, TypedDict, NoReturn, Generic

from timefred.singleton import Singleton
from timefred.log import log
from pdbpp import break_on_exc

class UNSET_TYPE(Singleton):
    def __repr__(self):
        return f'UNSET'
    
    def __bool__(self):
        return False
    

UNSET = UNSET_TYPE()


def updatedefault(obj: Any, name: str, mapping: Mapping):
    # noinspection PyUnresolvedReferences
    """
    >>> __fields__ = updatedefault(space, '__fields__', {'name': 'OpenAPI Validation'})
    >>> __fields__['name'] == 'OpenAPI Validation'
    """
    try:
        attr = getattr(obj, name)
    except AttributeError:
        setattr(obj, name, mapping)
        return getattr(obj, name)
    else:
        attr.update(**mapping)
        return attr


TFieldValue = TypeVar('TFieldValue')


class FieldData(TypedDict):
    value: TFieldValue
    cached: TFieldValue


class HasFields(Protocol[TFieldValue]):
    __fields__: dict[str, FieldData]

class DefaultFactory(Protocol[TFieldValue]):
    def __call__(self) -> TFieldValue:
        ...

class Cast(Protocol[TFieldValue]):
    def __call__(self, value: TFieldValue) -> TFieldValue:
        ...


class Field(Generic[TFieldValue]):
    """field_data['cached'] > field_data['value'] > default > default_factory"""
    def __init__(self,
                 default_factory: DefaultFactory[TFieldValue] = UNSET,
                 *,
                 default: TFieldValue = UNSET,
                 cast: Cast[TFieldValue] = UNSET,
                 optional=False,
                 cache=True
                 ):
        self.default = default
        self.default_factory = default_factory
        self.cast = cast
        self.should_cache = cache
        self.optional = optional
    
    def __set_name__(self, instance_cls: Type[HasFields], name: str):
        self.name = name
    
    def __call__(self, method: Callable) -> "Field":
        """Allows for using Field as a decorator with args, e.g `Field(optional=True)`"""
        if not callable(method):
            raise TypeError(("A Field instance was called. "
                             "Did you mean to call @Field as a method decorator?"))
        self.default_factory = method
        return self
    
    def get_set_default_instance_field_data(self, instance: HasFields, default_field_data: FieldData) -> FieldData:
        if not hasattr(instance, '__fields__'):
            setattr(instance, '__fields__', {self.name: default_field_data})
        elif self.name not in instance.__fields__:
            instance.__fields__[self.name] = default_field_data
        return instance.__fields__[self.name]
    
    def set_instance_field_data(self, instance: HasFields, field_data: FieldData) -> NoReturn:
        if not hasattr(instance, '__fields__'):
            setattr(instance, '__fields__', {self.name: field_data})
        else:
            instance.__fields__[self.name] = field_data
            
    def _repred_attrs(self) -> dict:
        default_factory_repr = getattr(self.default_factory, '__qualname__', self.default_factory)
        cast_repr = getattr(self.cast, '__qualname__', self.cast)
        attrs = dict(default=self.default,
                     default_factory=default_factory_repr,
                     cast=cast_repr,
                     optional=self.optional,
                     cache=self.should_cache)
        return attrs
    
    # def __repr__(self):
    #     return f"{self.__class__.__qualname__}⟨{self.name!r}⟩({', '.join([f'{k}={v}' for k, v in self._repred_attrs().items()])})"
    # @break_on_exc
    def __get__(self, instance: HasFields, instance_cls: Type[HasFields]) -> TFieldValue:
        field_data = self.get_set_default_instance_field_data(instance, {'value': UNSET, 'cached': UNSET})
        if self.should_cache and field_data['cached'] is not UNSET:
            return field_data['cached']
        
        value = field_data['value']
        if value is UNSET:
            if self.default is UNSET:
                if self.default_factory is UNSET:
                    if not self.optional:
                        raise AttributeError(f"{instance_cls.__qualname__}.{self.name} is unset, has no default value nor default_factory, and is not optional")
                else:
                    value = self.default_factory()
            else:
                value = self.default
        
        if self.cast and value is not UNSET:
            value = self.cast(value)
        
        if self.should_cache:
            instance.__fields__[self.name]['cached'] = value
        return value
    
    def __set__(self, instance: HasFields, value):
        # log.debug(f"setting {instance}.__fields__[ {self.name!r} ] = {value!r}")
        self.set_instance_field_data(instance, {'value': value, 'cached': UNSET})
        # if not hasattr(instance, '__fields__'):
        #     setattr(instance, '__fields__', {self.name: {'value': value, 'cached': UNSET}})
        # elif self.name not in instance.__fields__:
        #     instance.__fields__[self.name] = {'value': value, 'cached': UNSET}
        # else:
        #     instance.__fields__[self.name]['cached'] = UNSET
        #     # assert instance.__fields__[self.name]['cached'] is UNSET, f"{instance.__fields__[self.name]['cached']!r} is not UNSET"
        #     instance.__fields__[self.name]['value'] = value
    
    def __delete__(self, instance: HasFields):
        # log.debug(f"deleting {instance}.__fields__[ {self.name!r} ]")
        self.set_instance_field_data(instance, {'value': UNSET, 'cached': UNSET})
        # if not hasattr(instance, '__fields__'):
        #     setattr(instance, '__fields__', {self.name: {'value': UNSET, 'cached': UNSET}})
        # elif self.name not in instance.__fields__:
        #     instance.__fields__[self.name] = {'value': UNSET, 'cached': UNSET}
        # else:
        #     instance.__fields__[self.name]['cached'] = UNSET
        #     instance.__fields__[self.name]['value'] = UNSET
    
    def _unset_cache(self, instance: HasFields):
        if self.should_cache:
            field_data = instance.__fields__[self.name]
            field_data['cached'] = UNSET
            # assert field_data['cached'] is UNSET
            # assert instance.__fields__[self.name]['cached'] is UNSET
            # log.debug(f"cleared cache of {instance}.__fields__[ {self.name!r} ]",
            #           # f"it's now: {instance.__fields__[self.name]['cached']!r}"
            #           )
            # if instance.__fields__[self.name]['cached'] is not UNSET:
            #     breakpoint()