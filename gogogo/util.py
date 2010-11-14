import json

from gogogo import Position

class GoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'as_json'):
            return o.as_json()
        return super(GoJSONEncoder, self).default(o)
