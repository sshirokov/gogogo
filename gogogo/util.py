import json

from gogogo import Position

class GoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'as_json'):
            return o.as_json()
        return super(GoJSONEncoder, self).default(o)

def board_object_hook(d):
    if '__type__' in d:
        o_type = d.pop('__type__')
        Class = getattr(
            __import__('gogogo', globals(), locals(), [str(o_type)]),
            o_type,
            d
        )
        return Class.deserialize(**d)
    return d
