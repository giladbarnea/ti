import inspect
import os
import typing
from functools import wraps
from typing import Union, Any, Type, Optional, Callable, ForwardRef

from pdbpp import break_on_exc, rerun_and_break_on_exc

SHOULD_ANNOTATE = os.environ.get('TF_FEATURE_DIKT_ANNOTATE_GETATTR', 'false').lower() in ('1', 'yes', 'true')

UNSET = object()


def gettype(x: Union[type, Type[Any]]) -> type:
    if type(x) is type:
        # This includes gettype(type) and gettype(dict)
        return x
    # gettype(dict()) -> dict
    return type(x)


def trunc_mro(t) -> list[type]:
    t_mro = gettype(t).mro()
    t_mro.remove(object)
    return t_mro


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


def extract_initable(t: type) -> Optional[Callable[..., type]]:
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


def mro(t) -> list[type]:
    return gettype(t).mro()


Annotated = Any
Annotatable = Callable[[ForwardRef('Dikt'), Any], Annotated]

def annotate(maybe_method: Annotatable = None, *, set_in_self=False) -> Annotatable:
    def _annotate(method: Annotatable = None) -> Annotatable:
        @wraps(method)
        def decorator(self: ForwardRef('Dikt'), item: Any) -> Annotated:
            if item == '__rich_repr__':
                return lambda: repr(self)

            rv = method(self, item)

            if not SHOULD_ANNOTATE:
                return None if rv is UNSET else rv

            if item.startswith('_'):
                return rv

            annotations = self.__safe_annotations__
            if item not in annotations:
                if rv is UNSET:
                    raise NotImplementedError("This shouldn't happen?", locals())
                return rv

            annotation = annotations[item]
            initable = extract_initable(annotation)

            if type(rv) is initable:
                return rv

            if rv is UNSET:
                constructed_val = initable()
            else:
                try:
                    constructed_val = initable(rv)
                except TypeError as e:
                    raise TypeError(f"{e}. Tried to construct a {initable.__qualname__}({repr(rv)})") from None

            if set_in_self:
                self.__setattr__(item, constructed_val)

            return constructed_val

        return decorator

    if callable(maybe_method):
        return _annotate(maybe_method)

    return _annotate
