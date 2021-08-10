from types import GenericAlias
from typing import Any

from timefred.dikt.diktutils import UNSET, annotate, SHOULD_ANNOTATE, extract_initable


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
        raise NotImplementedError()

    def __class_getitem__(cls, item: Any) -> GenericAlias:
        cls.__annotations__.update(item)
        return super().__class_getitem__(item)

    # def update(self, mapping, **kwargs) -> None:
    #     for k, v in {**dict(mapping), **kwargs}.items():
    #         # maybe this is redundant with __setitem__ override?
    #         # setattr(self, k, v)
    #     super().update(mapping, **kwargs)

    def __repr__(self) -> str:
        return self.repr()

    @classmethod
    def __safe_annotations(cls):
        try:
            return cls.__annotations__
        except AttributeError:
            return dict()

    @annotate(set_in_self=True)
    def __getattribute__(self, item):
        """Makes d.foo return d['foo']"""
        try:
            return super().__getitem__(item)
        except KeyError as e:
            return super().__getattribute__(item)

    def __setattr__(self, name: str, value) -> None:
        """Makes d.foo = 'bar' also set d['foo']"""
        # print(f'__setattr__({self = } | {name = } | {value = })')
        super().__setattr__(name, value)
        self[name] = value

    # def __setitem__(self, k, v) -> None:
    #     """Makes d['foo'] = 'bar' set d.foo"""
    #     super().__setitem__(k, v)
    #     setattr(self, k, v)

class DefaultDikt(BaseDikt):
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
    __cache__: BaseDikt

    def __init__(self, mapping=(), **kwargs) -> None:
        super().__init__({**{'__cache__': BaseDikt()}, **dict(mapping, **kwargs)})
        # self.refresh()

    # todo: unused and should delete because done lazily via dunders
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

    # todo: unused and should delete because done lazily via dunders
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
