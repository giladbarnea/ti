from typing import Union, Any, Type

_builtin_scalars = frozenset({str, bytes, bytearray, int, float, complex,
                              bool, type(None)})


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


def mro(t) -> list[type]:
    return gettype(t).mro()
