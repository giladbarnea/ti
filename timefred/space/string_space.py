from timefred.space import Space
class StringSpace(str, Space):  # keep order because repr
    def __new__(cls, seq='', **kwargs) -> str:
        """Necessary to prevent **kwargs from passing to str.__new__()"""
        inst = str.__new__(cls, seq)
        return inst
    
    def __init__(self, seq='', **kwargs) -> None:
        Space.__init__(self, **kwargs)
