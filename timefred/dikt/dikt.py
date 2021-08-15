import inspect
import sys
import typing
from collections.abc import Iterable
from contextlib import suppress
from functools import wraps
from typing import ForwardRef, Any, Callable, Optional


class UNSET_TYPE:
    def __repr__(self):
        return f'UNSET'

    def __bool__(self):
        return False


UNSET = UNSET_TYPE()

DONT_ANNOTATE = set(dir(dict)) | {'__annotations__', '__safe_annotations__', '__dict__', '__module__', '__weakref__'}

Annotated = Any
Annotatable = Callable[[ForwardRef('Dikt'), Any], Annotated]


class Field:
    def __init__(self, default_factory: Callable = UNSET, *, default=UNSET, optional=False):
        self.default_factory = default_factory
        self.default = default
        self.__cached_value__ = UNSET
        self.optional = optional

    def __set_name__(self, owner, name):
        self.name = name
        self.__private_name__ = f'__field_{name}'

    def __get__(self, instance, objtype=None):
        if self.__cached_value__ is not UNSET:
            return self.__cached_value__

        value = getattr(instance, self.__private_name__, UNSET)
        if value is UNSET:
            if self.default is UNSET and self.default_factory is UNSET:
                raise AttributeError(f"{objtype.__name__}.{self.name} is unset")

            if self.default is UNSET:
                value = self.default_factory()
            else:
                value = self.default

        if self.default_factory is UNSET:
            self.__cached_value__ = value
            return value

        constructed = self.default_factory(value)
        # setattr(instance, self.__private_name__, constructed)
        self.__cached_value__ = constructed
        return constructed

    def __set__(self, instance, value):
        self.__cached_value__ = UNSET
        setattr(instance, self.__private_name__, value)

    def __delete__(self, instance):
        self.__cached_value__ = UNSET
        delattr(instance, self.__private_name__)



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


class InternalState(BaseDikt):
    pass


class Dikt(BaseDikt):
    """
    Features:

    1. Attributes
        - setting is 2-way: setting ['key'] also sets .key, and setting .key sets ['key']
        - getting is 1-way: .key -> ['key'], and ['key'] -> ['key']
        - lazy with __getattr__
        - eager with update()
        - eager with __setattr__()
        - eager with __setitem__()

    2. Annotations | dikt.foo: Foo
        - constructs Foo() by default on __init__
        - dikt.foo = "hi"; isinstance(dikt.foo, Foo) -> True
        - update_by_annotation()

    3. dikt.bad is None

    """
    __cache__: ForwardRef('NestedDikt')


class DefaultDikt(Dikt):
    @annotate(set_in_self=True)
    def __getattr__(self, item):
        return UNSET


class NestedDikt(Dikt):
    @annotate(set_in_self=True)
    def __getattr__(self, item):
        return NestedDikt()


print()
