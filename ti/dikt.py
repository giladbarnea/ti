import typing
import inspect
from functools import wraps


def extract_initable(t):
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


def return_None_on(exc: typing.Type[BaseException]):
    def decorator(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except exc:
                return None
        return inner
    return decorator


@return_None_on(AttributeError)
def have_common_ancestor(t1, t2) -> bool:
    try:
        t1_mro = t1.mro()
    except AttributeError:
        t1_mro = type(t1).mro()

    try:
        t2_mro = t2.mro()
    except AttributeError:
        t2_mro = type(t2).mro()

    t1_mro = set(t1_mro) - {object}
    t2_mro = set(t2_mro) - {object}
    return bool(t1_mro & t2_mro)

class ValidatorError(TypeError): ...
class ConflictsAnnotation(ValidatorError): ...

class Dikt(dict):
    # TODO:
    #  inherit from Generic?
    #  if a key not in mapping, but in annotations (not optional), initialize
    def __init__(self, mapping=()) -> None:
        super().__init__(mapping)
        self.refresh()

    def update_by_annotation(self, k, v) -> bool:
        try:
            annotations = self.__class__.__annotations__
        except AttributeError:
            return False

        if k not in annotations:
            return False

        annotation = annotations[k]
        initable = extract_initable(annotation)
        if not initable:
            return False
        # if not have_common_ancestor(v, initable): # not good because str and XArrow
        #     raise ConflictsAnnotation(f'({type(self)}) | {k} = {repr(v)} is not an instance of {initable} (annotation: {annotation})')
        try:
            constructed_val = initable(v)
        except:
            return False

        self.update({k: constructed_val})
        return True

    def refresh(self):
        for k, v in self.items():
            if self.update_by_annotation(k, v):
                continue

            if isinstance(v, dict):
                self.update({k: Dikt(v)})
            else:
                self.update({k: v})


    def __repr__(self) -> str:
        name = self.__class__.__qualname__
        if not self:
            return f"{name}({{}})"
        rv = f"{name}({{\n    "
        max_key_len = max(map(len, self.keys()))
        for k, v in self.items():
            # if k.startswith('_'):
            # 	continue
            rv += f"{str(k).ljust(max_key_len, ' ')} : {repr(v).replace('    ', '        ')},\n    "
        rv += "})"
        return rv

    # def __getitem__(self, k):
    #     """Like `normal_dict.get('foo', None)`"""
    #     try:
    #         return super().__getitem__(k)
    #     except KeyError as e:
    #         return None

    def __getattr__(self, item):
        """Makes `d.foo` call `d['foo']`"""
        try:
            return self[item]
        except KeyError as e:
            if e.args[0] == '__rich_repr__':
                return lambda: repr(self)

    def __setattr__(self, name: str, value) -> None:
        super().__setattr__(name, value)
        self[name] = value
