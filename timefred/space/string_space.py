from timefred.space import Space
class StringSpace(str, Space):  # keep order because repr
    def __new__(cls, o, **kwargs):
        """Necessary to prevent **kwargs from passing to str.__new__()"""
        inst = str.__new__(cls, o)
        return inst
    
    def __init__(self, o, **kwargs) -> None:
        Space.__init__(self, **kwargs)
