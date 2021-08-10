import inspect
import sys
import os
import typing
from functools import wraps
from typing import Union, Any, Type, Optional, Callable, ForwardRef

DONT_ANNOTATE = set(dir(dict)) | {'__annotations__', '__safe_annotations__'}

SHOULD_ANNOTATE = os.environ.get('TF_FEATURE_DIKT_ANNOTATE_GETATTR', 'true').lower() in ('1', 'yes', 'true')

UNSET = object()

def resolve_forwardref(t: ForwardRef, cls):
    globalns = sys.modules[cls.__module__].__dict__.copy()
    globalns.setdefault(cls.__name__, cls)
    evaluated = t._evaluate(globalns, None, frozenset())
    return evaluated

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


from pdbpp import rerun_and_break_if_returns, break_on_return, break_before_call


# @break_before_call(condition=lambda *_args, **_kwargs: isinstance(_args[0], ForwardRef))
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
            # from timefred.dikt import Dikt, InternalState
            # DONT_ANNOTATE = set(dir(Dikt))
            if item == '__rich_repr__':
                return lambda: self

            rv = method(self, item)

            if not SHOULD_ANNOTATE:
                return None if rv is UNSET else rv

            if item in DONT_ANNOTATE:
                if rv is UNSET:
                    raise NotImplementedError(f"This shouldn't happen? {item = } in DONT_ANNOTATE, and rv is UNSET", locals())
                return rv


            # if isinstance(rv, InternalState):
            #     breakpoint()
            #     return rv

            # if item.startswith('_'):
            #     # otherwise self.__safe_annotations__ RecursionError
            #     print(rv, item)
            #     return rv

            annotations = self.__safe_annotations__
            if item not in annotations:
                if rv is UNSET:
                    raise NotImplementedError(f"This shouldn't happen? {item = } not in annotations, and rv is UNSET", locals())
                return rv

            annotation = annotations[item]
            if isinstance(annotation, ForwardRef):
                breakpoint()
                # cls = self.__class__
                # globalns = sys.modules[cls.__module__].__dict__.copy()
                # globalns.setdefault(cls.__name__, cls)
                # evaluated = annotation._evaluate(globalns, None, frozenset())
            initable = extract_initable(annotation, self)

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
