import json

import bottle
from bottle import Bottle

from gogogo.game import Game, GameError


app = Bottle(autojson=False)
def dict2json(o):
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
               'POST': [{'/game/create/': 'Create a new game'}],
            },
}

class ParamFilter(object):
    def __init__(self, **kwargs):
        self.filters = kwargs

    def __wrapped__(self, *args, **kwargs):
        [kwargs.update({key: self.filters.get(key)(val)})
         for (key, val) in kwargs.items()
         if self.filters.has_key(key)]
        return self.fn(*args, **kwargs)

    def __call__(self, fn):
        self.fn = fn
        return self.__wrapped__

def with_game(fn):
    def make_game(game):
        try: return Game(game)
        except GameError: raise bottle.HTTPResponse({'message': 'Game not found'}, 404)
    return ParamFilter(game=make_game)(fn)

@app.post('/game/:game#[0-9a-f]+#/player/create/', name='game-player-create')
@with_game
def register_player(game):
    try: data = json.loads(bottle.request.body.read())
    except ValueError: raise bottle.HTTPResponse({'message': "JSON seems invalid"}, 400)
    print "I got data:", data
    print "For game:", game

@app.get('/game/:game#[0-9a-f]+#/branch/', name='game-branch-index')
@with_game
def branches(game):
    return {'message': '',
            'data': game.branches()}

@app.post('/game/:game#[0-9a-f]+#/branch/create/', name='game-branche-create')
@with_game
def create_branch(game):
    pass

@app.get('/game/:game#[0-9a-f]+#/branch/:branch/', name='game-branch')
@with_game
def game(game, branch):
    pass

@app.get('/game/:game#[0-9a-f]+#/', name='game-index')
@with_game
def game(game):
    return {'message': '',
            'turn': game.board.player_turn(),
            'data': game.board.take_snapshot()}

@app.post('/game/create/', name='game-create')
def new_game():
    game = Game(create=True)
    bottle.redirect(app.get_url('game-index', name=game.name))

@app.get('/', name='index')
def index():
    return routes


def run(addr='localhost', port=9090, **kwargs):
    bottle.debug(kwargs.pop('debug', False))
    bottle.run(app=app, host=addr, port=port,
               **dict({'reloader': kwargs.pop('reload', False), 
                       'interval': kwargs.pop('reload_interval', 1)},
                      **kwargs))
