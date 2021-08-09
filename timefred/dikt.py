import inspect
import os
import typing
from functools import wraps
from typing import Any, Type, Union, Optional, ForwardRef, Callable

SHOULD_ANNOTATE = os.environ.get('TF_FEATURE_DIKT_ANNOTATE_GETATTR', 'false').lower() in ('1', 'yes', 'true')
# os.environ['PREBREAK_PATCH_PRINT'] = '1'
# from timefred import prebreak

UNSET = object()


def extract_initable(t: type) -> Optional[Callable[Optional[Any], type]]:
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
    origin = typing.get_origin(t)
    if origin is None:  # Any
        if inspect.getmodule(t) is typing:
            return None
        return t
    if origin is not typing.Union:
        return origin

    # origin is Union or Optional[foo]
    origins = [a for a in typing.get_args(t) if a != type(None)]
    if len(origins) == 1:
        origin = origins[0]
        return extract_initable(origin)
    return None


# unused
def return_None_on(exc: Type[BaseException]):
    def decorator(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except exc:
                return None

        return inner

    return decorator


# unused
def gettype(x: Union[type, Type[Any]]) -> type:
    if type(x) is type:
        # This includes gettype(type) and gettype(dict)
        return x
    # gettype(dict()) -> dict
    return type(x)


# unused
def mro(t) -> list[type]:
    return gettype(t).mro()


# unused
def trunc_mro(t) -> list[type]:
    t_mro = gettype(t).mro()
    t_mro.remove(object)
    return t_mro


@return_None_on(AttributeError)  # unused
def have_common_ancestor(t1, t2) -> bool:
    # t1_mro = mro(t1)
    # t2_mro = mro(t2)
    #
    # t1_truncated_mro = set(t1_mro) - {object}
    # t2_truncated_mro = set(t2_mro) - {object}

    t1_truncated_mro = trunc_mro(t1)
    t2_truncated_mro = trunc_mro(t2)
    return bool(set(t1_truncated_mro) & set(t2_truncated_mro))


# unused
def strict_inherits_from(inst, t) -> bool:
    """
    >>> strict_inherits_from(dict(), dict)
    False
    >>> strict_inherits_from(dict, dict)
    False
    >>> strict_inherits_from(Dikt(), dict)
    True
    >>> strict_inherits_from(Dikt, dict) # Fails when Dikt metaclass is DiktMeta
    True
    """
    inst_type = gettype(inst)
    t_type = gettype(t)
    if not issubclass(inst_type, t_type):
        return False
    return inst_type is not t_type


Annotated = Any
Annotatable = Callable[[ForwardRef('Dikt'), Any], Annotated]


def annotate(maybe_method: Annotatable = None, *, set_in_self=False) -> Annotatable:
    def _annotate(method: Annotatable = None) -> Annotatable:
        @wraps(method)
        def decorator(self: 'Dikt', item: Any) -> Annotated:
            if item == '__rich_repr__':
                return lambda: repr(self)

            rv = method(self, item)

            if not SHOULD_ANNOTATE:
                return None if rv is UNSET else rv

            if item.startswith('_'):
                return rv
            annotations = self.__annotations__
            # annotations = self.__class__.__annotations__
            if item in annotations:
                annotation = annotations[item]
                initable = extract_initable(annotation)
                type_args = typing.get_args(annotation)
            else:
                initable = lambda _=None: _
                type_args = tuple()

            if type(rv) is initable:
                return rv

            if rv is UNSET:
                constructed_val = initable()
            else:
                constructed_val = initable(rv)

            if set_in_self:
                # Assumes `__setattr__` override sets ['foo']
                self.__setattr__(item, constructed_val)

            if type_args:
                try:
                    constructed_val.__annotations__.update(dict(*type_args))
                    constructed_val.refresh()
                except Exception as e:
                    # This assumes constructed_val is a Dikt :/
                    print(e.__class__.__qualname__, e)
                    breakpoint()

            return constructed_val

        return decorator

    if callable(maybe_method):
        return _annotate(maybe_method)

    return _annotate


class ValidatorError(TypeError): ...


class ConflictsAnnotation(ValidatorError): ...


class DiktMeta(type):
    def __getitem__(self, item):
        self.__annotations__.update(item)
        for k, v in item.items():
            setattr(self, k, v)
        return item


class Field:
    def __init__(self, default_factory=UNSET):
        self.default_factory = default_factory


class BaseDikt(dict):
    __config__: dict

    def repr(self, *, private=False, dunder=False, methods=False):
        name = self.__class__.__qualname__
        if not self:
            return f"{name}({{}})"
        rv = f"{name}({{\n  "
        max_key_len = max(map(len, self.keys()))
        for k, v in self.items():
            if k.startswith('_') and not private:
                continue
            if k.startswith('__') and not dunder:
                continue
            rv += f"{str(k).ljust(max_key_len, ' ')} : {repr(v).replace('  ', '    ')},\n  "
        rv += "})"
        return rv

    def dict(self):
        rv = {}
        annotations = self.__safe_annotations()
        self_dict = self.__dict__
        breakpoint()

    # def update(self, mapping, **kwargs) -> None:
    #     for k, v in {**dict(mapping), **kwargs}.items():
    #         # maybe this is redundant with __setitem__ override?
    #         # setattr(self, k, v)
    #     super().update(mapping, **kwargs)

    # def __repr__(self) -> str:
    # return self.repr()

    @classmethod
    def __safe_annotations(cls):
        try:
            return cls.__annotations__
        except AttributeError:
            return dict()

    # def __getattribute__(self, name: str) -> Any:
    #     value = super().__getattribute__(name)
    #     if not SHOULD_ANNOTATE:
    #         return value
    #     if name == '__annotations__':
    #         return value
    #     if name not in self.__annotations__:
    #         return value
    #     annotation = self.__annotations__[name]
    #     initable = extract_initable(annotation)
    #     # TODO: build defaults from annotation:
    #     if not initable or isinstance(value, initable):
    #         return value
    #     constructed = initable(value)
    #     return constructed

    # def __getitem__(self, k):
    #     print(f'__getitem__({self = } | {k = })')
    #     return super().__getitem__(k)

    @annotate(set_in_self=True)
    def __getattribute__(self, item):
        """Makes d.foo return d['foo']"""
        try:
            return super().__getitem__(item)
        except KeyError as e:
            return super().__getattribute__(item)
            # return UNSET
        # rv =
        # return rv
        # return UNSET
        # try:
        #     rv = super().__getattribute__(item)
        #     return rv
        # except AttributeError:
        #     return UNSET

    # @annotate(set_in_self=True)
    # def __getattr__(self, item):
    #     """Makes d.foo return d['foo']"""
    #     print(f'__getattr__({self = } | {item = })')
    #     if item in self:
    #         return self[item]
    #     return UNSET

    def __setattr__(self, name: str, value) -> None:
        """Makes d.foo = 'bar' also set d['foo']"""
        print(f'__setattr__({self = } | {name = } | {value = })')
        super().__setattr__(name, value)
        self[name] = value

    # def __setitem__(self, k, v) -> None:
    #     """Makes d['foo'] = 'bar' set d.foo"""
    #     super().__setitem__(k, v)
    #     setattr(self, k, v)


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
    __cache__: BaseDikt

    def __init__(self, mapping=(), **kwargs) -> None:
        super().__init__({**{'__cache__': BaseDikt()}, **dict(mapping, **kwargs)})
        # self.refresh()

    def refresh(self):
        # self_keys = set()
        for k, v in self.items():
            # self_keys.add(k)
            if self.update_by_annotation(k, v):
                continue

            # if isinstance(v, dict) and strict_inherits_from(v, dict):
            if type(v) is dict:  # Wrap only raw dict, not subclasses
                self.update({k: Dikt(v)})
            else:  # is this necessary? maybe, because update also sets attr
                self.update({k: v})

        # annotations = self.__safe_annotations()
        # for annotation_name in set(annotations) - self_keys:
        #     self.update_by_annotation(annotation_name)

    def update_by_annotation(self, k, v=UNSET) -> bool:
        """Returns True if v's type was updated to match, or already was of the annotated type"""
        if not SHOULD_ANNOTATE:
            return False

        annotations = self.__class__.__annotations__

        if k not in annotations:
            return False

        annotation = annotations[k]
        initable = extract_initable(annotation)
        if not initable:
            return False

        if type(v) is initable:
            return True
        try:
            if v is UNSET:
                # v = getattr(self.__class__, k)
                constructed_val = initable()
            else:
                constructed_val = initable(v)
            # constructed_val = initable(v)
        except Exception as e:
            # if not v and getattr(self.__class__, k):
            # 	# Default was specified on class level
            # 	breakpoint()
            # 	self.update({k: getattr(self.__class__, k)})
            # 	return True
            return False

        self.update({k: constructed_val})
        return True
