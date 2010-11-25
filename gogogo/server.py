import bottle
from bottle import Bottle

app = Bottle(autojson=False)
def dict2json(o):
    import json
    from gogogo.util import GoJSONEncoder
    bottle.response.content_type = 'application/json'
    return json.dumps(o, cls=GoJSONEncoder)
app.add_filter(dict, dict2json)

routes = {
    'root': {
               'GET': [{'/': 'home'}]
            },
    'game': {
               'GET': [{'/game/{game}/': 'Load game'}],
               'POST': [{'/game/new/': 'Create a new game'}],
            },
}

@app.route('/game/:name#[0-9a-f]+#/')
def game(name):
    from gogogo.game import Game
    game = Game(name)
    return game.board.take_snapshot()

@app.route('/')
def index():
    return routes


def run(addr='localhost', port=9090, **kwargs):
    bottle.debug(kwargs.pop('debug', False))
    bottle.run(app=app, host=addr, port=port,
               **dict({'reloader': kwargs.pop('reload', False), 
                       'interval': kwargs.pop('reload_interval', 1)},
                      **kwargs))
