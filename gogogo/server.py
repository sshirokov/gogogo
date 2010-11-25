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

@app.post('/game/:name#[0-9a-f]+#/player/', name='game-register-player')
def register_player(game):
    pass

@app.post('/game/:name#[0-9a-f]+#/move/:player#[0-9a-f]+#/', name='game-move')
def move(game, player):
    pass

@app.get('/game/:name#[0-9a-f]+#/branches/', name='game-branches')
def branches(game):
    pass

@app.get('/game/:name#[0-9a-f]+#/branch/', name='game-branch-current')
def current_branch(game):
    pass

@app.post('/game/:name#[0-9a-f]+#/branches/create/', name='game-branches-create')
def create_branch(game):
    pass

@app.post('/game/:name#[0-9a-f]+#/branches/switch/', name='game-branches-switch')
def switch_branch(game):
    pass

@app.get('/game/:name#[0-9a-f]+#/branch/:branch/', name='game-branch')
def game(name, branch):
    pass

@app.get('/game/:name#[0-9a-f]+#/', name='game')
def game(name):
    try:
        game = Game(name)
        return game.board.take_snapshot()
    except GameError:
        bottle.response.content_type = 'application/json'
        bottle.response.status = 404
        return {'message': 'Game does not exist'}

@app.post('/game/create/', name='game-create')
def new_game():
    game = Game(create=True)
    bottle.redirect(app.get_url('game', name=game.name))

@app.get('/', name='index')
def index():
    return routes


def run(addr='localhost', port=9090, **kwargs):
    bottle.debug(kwargs.pop('debug', False))
    bottle.run(app=app, host=addr, port=port,
               **dict({'reloader': kwargs.pop('reload', False), 
                       'interval': kwargs.pop('reload_interval', 1)},
                      **kwargs))
