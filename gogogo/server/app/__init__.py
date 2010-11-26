import json
import bottle
from bottle import Bottle

app = Bottle(autojson=False)
def dict2json(o):
    from gogogo.util import GoJSONEncoder
    bottle.response.content_type = 'application/json'
    return json.dumps(o, cls=GoJSONEncoder)
app.add_filter(dict, dict2json)
