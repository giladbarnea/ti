import inspect
import sys
import typing
from collections.abc import Iterable, MutableMapping
from contextlib import suppress
from functools import wraps
from typing import ForwardRef, Any, Callable, Optional, Type, TypeVar, Generic, NewType


class UNSET_TYPE:
    def __repr__(self):
        return f'UNSET'

    def __bool__(self):
        return False


UNSET = UNSET_TYPE()

DONT_ANNOTATE = set(dir(dict)) | {'__annotations__', '__safe_annotations__', '__dict__', '__module__', '__weakref__'}

Annotated = Any
Annotatable = Callable[[ForwardRef('Dikt'), Any], Annotated]

Instance = NewType('Instance', object)
SupportsItemAssignment = NewType('SupportsItemAssignment', MutableMapping)

_T = TypeVar('_T')


class UnsetFieldError(AttributeError): ...


class AnnotationMismatchError(TypeError): ...


class Field(Generic[_T]):
    """getattr(instance, self.private_name, UNSET), then
    self.default_value > self.default_factory > classvar annotation > instance.__getitem__.
    Caches in self.cached_value (In Field instance's cached_value)
    """

    def __init__(self,
                 default_factory: Callable[..., _T] = UNSET,
                 *,
                 default=UNSET,
                 type: Type[_T] = UNSET,
                 name: str = UNSET,
                 validator: Callable[[Type[_T]], bool] = UNSET,
                 optional=False,
                 strict=False
                 ):
        self.default_factory = default_factory
        self.default_value = default
        self.type: Type[_T] = type
        self.cached_value: _T = UNSET
        self.validator: Callable[[Type[_T]], bool] = validator
        self.optional = optional
        self.strict = strict
        if name:
            self.name = name
            self.private_name = f'__field_{name}'
        # if self.strict and not isinstance(value, annotation := instance.__annotations__[self.name]):
        #     raise AnnotationMismatchError(f"{objtype.__name__}.{self.name}'s type ({type(value)}) does not match its annotation ({annotation})")

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f'__field_{name}'

    def cache(__get__: Callable[[ForwardRef('Field'), Instance, Optional[Type[Instance]]], _T]):
        def cache_decorator(field: ForwardRef('Field'), instance: Instance, objtype: Type[Instance] = None) -> _T:
            if field.cached_value is not UNSET:
                return field.cached_value
            rv = __get__(field, instance, objtype)
            field.cached_value = rv
            return rv

        return cache_decorator

    @cache
    def __get__(self, instance: Instance, objtype: Type[Instance] = None) -> _T:
        value = getattr(instance, self.private_name, UNSET)
        if value is UNSET:
            if self.default_value is UNSET:
                if self.default_factory is UNSET:
                    raise UnsetFieldError(f"{objtype.__name__}.{self.name} is unset")

                value = self.default_factory()
            else:
                value = self.default_value

        if self.default_factory is UNSET:
            # Type coersion: annotation works like default_factory
            try:
                annotation = instance.__annotations__.get(self.name)
            except AttributeError:
                # Happens once per instance
                instance.__annotations__ = dict()
                return value
            if annotation is not None:
                return annotation(value)
            return value
        return self.default_factory(value)

    def __set__(self, instance: Instance, value):
        self.cached_value = UNSET
        setattr(instance, self.private_name, value)

    def __delete__(self, instance: Instance):
        self.cached_value = UNSET
        delattr(instance, self.private_name)


class DiktField(Field):
    """Caches and sets value in instance[self.name].
    Makes instance['foo'] and instance.foo indistinguishable.
    """

    def cache(__get__: Callable[[ForwardRef('DiktField'), SupportsItemAssignment, MutableMapping], _T]):
        def cache_decorator(field: ForwardRef('DiktField'), instance: SupportsItemAssignment, objtype: MutableMapping = None) -> _T:
            if field.cached_value is not UNSET:
                # print('DiktField returning cached')
                return field.cached_value
            try:
                rv = __get__(field, instance, objtype)
            except UnsetFieldError as uf:
                try:
                    rv = instance[field.name]
                except (KeyError, TypeError) as key_or_typeerror:
                    if isinstance(key_or_typeerror, TypeError) and 'does not support item assignment' not in str(key_or_typeerror):
                        import logging
                        logging.warning(f"TypeError not because item assignment: {key_or_typeerror}")
                    raise uf from None

            field.cached_value = rv
            instance[field.name] = rv
            return rv

        return cache_decorator

    @cache
    def __get__(self, instance: SupportsItemAssignment, objtype: MutableMapping = None) -> _T:
        # print(f'DiktField __get__(...)')
        return super().__get__(instance, objtype)


def extract_initable(t: type, inst=None) -> Optional[Callable[..., type]]:
    """Extract e.g `dict` from `Optional[dict]`.
    Returns None if non-extractable.

    >>> from typing import Optional, Dict, List
    >>> ei = extract_initable

    >>> ei(List[str]) is ei(List) is ei(list) is ei(Optional[List[str]]) is list
    True

    >>> ei(Dict[str,int]) is ei(Dict) is ei(dict) is ei(Optional[Dict[str,int]]) is dict
    True

    >>> class Foo: ...
    >>> ei(Foo) is Foo
    True
    """
    if isinstance(t, ForwardRef):
        evaluated = resolve_forwardref(t, inst.__class__)
        return extract_initable(evaluated)
        # breakpoint()
        # return evaluated
    origin = typing.get_origin(t)
    if origin is None:  # Any
        if inspect.getmodule(t) is typing:
            return None
        return t

    type_args = typing.get_args(t)
    if origin is not typing.Union:
        if issubclass(origin, Iterable) and type_args:
            if len(type_args) > 1:
                raise NotImplementedError(f"{t = }, {type_args = }, more than 1 type_args")
            return lambda *args: origin(map(type_args[0], *args))
        return origin

    # origin is Union or Optional[foo]
    origins = [a for a in typing.get_args(t) if a != type(None)]
    if len(origins) == 1:
        origin = origins[0]
        return extract_initable(origin)
    return None


# @cache
def resolve_forwardref(t: ForwardRef, cls):
    # globalns = sys.modules[cls.__module__].__dict__.copy()
    # globalns.setdefault(cls.__name__, cls)
    # try:
    #     evaluated = t._evaluate(globalns, None, frozenset())
    # except NameError as e:
    #     return resolve_forwardref(t, cls.mro()[1])
    # return evaluated
    try:
        return sys.modules[cls.__module__].__dict__[t.__forward_arg__]
    except KeyError:
        return resolve_forwardref(t, cls.mro()[1])


def annotate(maybe_method: Annotatable = None, *, set_in_self=False) -> Annotatable:
    def _annotate(method: Annotatable = None) -> Annotatable:

        @wraps(method)
        def decorator(self: ForwardRef('Dikt'), item: Any) -> Annotated:
            # from timefred.dikt import Dikt, InternalState
            # DONT_ANNOTATE = set(dir(Dikt))
            if item == '__rich_repr__':
                return lambda: self
            if item not in DONT_ANNOTATE | {'shape'}:
                ...
                # pr(self, item)

            rv = method(self, item)

            if item in DONT_ANNOTATE:
                if rv is UNSET:
                    raise NotImplementedError(f"This shouldn't happen? {item = } in DONT_ANNOTATE, and rv is UNSET", locals())
                return rv

            annotations = self.__safe_annotations__
            if item not in annotations:
                cls = self.__class__
                clsvar_val = getattr(cls, item, UNSET)
                if rv is UNSET:
                    raise NotImplementedError(f"This shouldn't happen? {item = } not in annotations, and rv is UNSET", locals())
                return rv

            annotation = annotations[item]
            if isinstance(annotation, ForwardRef):
                breakpoint()  # Shouldn't happen because BaseDikt.__new__

            if isinstance(annotation, Field):
                print()

            initable = extract_initable(annotation, self)

            rv_type = type(rv)
            if rv_type is initable:
                return rv

            with suppress(AttributeError):
                if rv_type.__qualname__ is initable.default_factory.__annotations__['return']:
                    return rv

            if rv is UNSET:
                constructed_val = initable()
            else:
                try:
                    constructed_val = initable(rv)
                except TypeError as e:
                    name = getattr(initable, '__qualname__', repr(initable))
                    raise TypeError(f"{e}. Tried to construct a {name}({repr(rv)})") from None

            if set_in_self:
                self.__setattr__(item, constructed_val)

            return constructed_val

        return decorator

    if callable(maybe_method):
        return _annotate(maybe_method)

    return _annotate


class DiktMeta(type):
    def __getitem__(self, item):
        self.__annotations__.update(item)
        for k, v in item.items():
            setattr(self, k, v)
        return item


class BaseDikt(dict):
    # __config__: ForwardRef('NestedDikt')
    # __items__: ForwardRef('NestedDikt')
    # __attrs__: ForwardRef('NestedDikt')
    # __exclude__ = set()

    def __new__(cls, *args: Any, **kwargs: Any):
        for item, annotation in cls.__annotations__.items():
            if isinstance(annotation, ForwardRef):
                evaluated = resolve_forwardref(annotation, cls)
                cls.__annotations__[item] = evaluated

        inst = super().__new__(cls, *args, **kwargs)
        return inst

    # def __repr__(self, *, private=False, dunder=False, methods=False):
    #     name = self.__class__.__qualname__
    #     if not self:
    #         return f"{name}({{}})"
    #     rv = f"{name}({{\n  "
    #     max_key_len = max(map(len, self.keys()))
    #     for k, v in self.items():
    #         if k.startswith('_') and not private:
    #             continue
    #         if k.startswith('__') and not dunder:
    #             continue
    #         rv += f"{str(k).ljust(max_key_len, ' ')} : {repr(v).replace('  ', '    ')},\n  "
    #     rv += "})"
    #     return rv

    def dict(self):
        rv = {}
        annotations = self.__safe_annotations__
        self_dict = self.__dict__
        raise NotImplementedError()

    def __iter__(self):
        """
        so `dict(model)` works.
        pydantic/main.py#L733
        """
        yield from self.__dict__.items()

    def __class_getitem__(cls, item):
        cls.__annotations__.update(item)
        return super().__class_getitem__(item)

    # def update(self, mapping, **kwargs) -> None:
    #     for k, v in {**dict(mapping), **kwargs}.items():
    #         # maybe this is redundant with __setitem__ override?
    #         # setattr(self, k, v)
    #     super().update(mapping, **kwargs)

    @property
    def __safe_annotations__(self) -> dict:
        try:
            return self.__annotations__
        except AttributeError:
            return dict()

    @annotate(set_in_self=True)
    def __getattribute__(self, name):
        """Makes d.foo return d['foo']"""
        try:
            item = super().__getitem__(name)
            return item
        except KeyError as e:
            attr = super().__getattribute__(name)
            return attr

    def __setattr__(self, name: str, value) -> None:
        """Makes d.foo = 'bar' also set d['foo']"""
        super().__setattr__(name, value)
        self[name] = value


class Dikt(BaseDikt):
    """
    Features:

    1. Attributes
        - setting is 2-way: setting ['key'] also sets .key, and setting .key sets ['key']
        - getting is 1-way: .key -> ['key'], and ['key'] -> ['key']

    2. Annotations | dikt.foo: Foo
        - dikt.foo = "hi"; isinstance(dikt.foo, Foo) -> True

    """
    __cache__: ForwardRef('NestedDikt')


class DefaultDikt(Dikt):
    """
    Annotations | dikt.foo: Foo
        - dikt.foo == Foo() -> True
    """

    @annotate(set_in_self=True)
    def __getattr__(self, item):
        return UNSET


class NestedDikt(Dikt):
    """
    Attributes
        dikt.bad.nope == NestedDikt()
    """

    @annotate(set_in_self=True)
    def __getattr__(self, item):
        return NestedDikt()


print()
