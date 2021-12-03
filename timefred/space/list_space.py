from typing import TypeVar, Union
from collections.abc import Iterable
from timefred.space import Space, TypedSpace
from .space import IGNORED_ATTRS

LIST_SPACE_V = TypeVar('LIST_SPACE_V')


class ListSpace(Space, list[LIST_SPACE_V]):
    def __init__(self, iterable: Iterable[LIST_SPACE_V] = (), **kwargs) -> None:
        """Necessary for passed **kwargs to get setattred"""
        list.__init__(self, iterable)
        Space.__init__(self, **kwargs)


TYPED_LIST_SPACE_V = TypeVar('TYPED_LIST_SPACE_V')


class TypedListSpace(ListSpace[TYPED_LIST_SPACE_V],
                     TypedSpace[Union[int, slice], TYPED_LIST_SPACE_V]
                     ):
    # def __getitem__(self, name: Union[int, slice]) -> LIST_SPACE_V:
    def __getitem__(self, name):
        """Ensures self[name] is of __default_factory__"""
        try:
            # Should setattr this as well?
            value = list.__getitem__(self, name)
        except (KeyError, IndexError):
            raise
        else:
            if not isinstance(value, self.__default_factory__):
                # todo (bug): activity[:] -> TypeError: unhashable type: 'slice'
                assert name not in self.__class__.DONT_SET_KEYS | IGNORED_ATTRS, \
                    (f"{self.__class__.__qualname__}.__getitem__({name!r}) returned {value!r} "
                     f"but it's not of type {self.__default_factory__.__qualname__} "
                     f"and it's in {self.__class__.DONT_SET_KEYS | IGNORED_ATTRS = }")
                constructed = self.__default_factory__(**value)
                list.__setitem__(self, name, constructed)
                return constructed
            return value
