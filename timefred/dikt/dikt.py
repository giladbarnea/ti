from typing import ForwardRef, Any

from timefred.dikt.diktutils import UNSET, annotate, resolve_forwardref


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
    __config__: ForwardRef('NestedDikt')
    __items__: ForwardRef('NestedDikt')
    __attrs__: ForwardRef('NestedDikt')

    def __new__(cls, *args: Any, **kwargs: Any):
        for item, annotation in cls.__annotations__.items():
            if isinstance(annotation, ForwardRef):
                evaluated = resolve_forwardref(annotation, cls)
                cls.__annotations__[item] = evaluated

        inst = super().__new__(cls, *args, **kwargs)
        return inst

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

    def __repr__(self) -> str:
        return self.repr()

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
