class ParamFilter(object):
    def __init__(self, **kwargs):
        self.filters = kwargs

    def __wrapped__(self, *args, **kwargs):
        [kwargs.update({key: self.filters.get(key)(val, kwargs)})
         for (key, val) in kwargs.items()
         if self.filters.has_key(key)]
        return self.fn(*args, **kwargs)

    def __call__(self, fn):
        self.fn = fn
        return self.__wrapped__
