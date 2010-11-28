import json

from gogogo import Position

class GoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'as_json'):
            return o.as_json()
        return super(GoJSONEncoder, self).default(o)

def _board_object_hook(d, replace=None):
    '''
    replace param in the form {prop, val}
    '''
    if '__type__' in d:
        o_type = d.pop('__type__')
        Class = getattr(
            __import__('gogogo', globals(), locals(), [str(o_type)]),
            o_type,
            d
        )
        obj = Class.deserialize(**d)
        [setattr(obj, name, val)
         for name, val in replace.items()]
        return obj
    return d

def make_board_object_hook(replace=None):
    return lambda d: _board_object_hook(d, replace)

def make_consuming_chain(*functions):
    '''
    Return a function that will call functions in sequence, passing the return down the chain of functions
    '''
    return reduce(lambda acc, f: lambda *args, **kwargs: f(acc(*args, **kwargs)), functions)

