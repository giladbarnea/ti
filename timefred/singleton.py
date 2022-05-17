class Singleton:
    def __new__(cls, *args, **kwargs):
        if hasattr(cls, '_inst'):
            return getattr(cls, '_inst')
        inst = super().__new__(cls)
        if args or kwargs:
            breakpoint()
        return inst

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            breakpoint()
        if hasattr(self.__class__, '_inst'):
            return
        setattr(self.__class__, '_inst', self)
    
    def __copy__(self):
        return self
    def __deepcopy__(self):
        return self
