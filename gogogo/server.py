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

@app.post('/game/:name#[0-9a-f]+#/player/create/', name='game-player-create')
def register_player(name):
    try: data = json.loads(bottle.request.body.read())
    except ValueError: raise bottle.HTTPResponse({'message': "JSON seems invalid"}, 400)
    print "I got data:", data

@app.get('/game/:name#[0-9a-f]+#/branch/', name='game-branch-index')
def branches(name):
    try:
        game = Game(name)
        return {'message': '',
                'data': game.branches()}
    except GameError:
        bottle.response.status = 404
        return {'message': 'Game does not exist'}

@app.post('/game/:name#[0-9a-f]+#/branch/create/', name='game-branche-create')
def create_branch(game):
    pass

@app.get('/game/:name#[0-9a-f]+#/branch/:branch/', name='game-branch')
def game(name, branch):
    pass

@app.get('/game/:name#[0-9a-f]+#/', name='game-index')
def game(name):
    try:
        game = Game(name)
        return {'message': '',
                'turn': game.board.player_turn(),
                'data': game.board.take_snapshot()}
    except GameError:
        bottle.response.status = 404
        return {'message': 'Game does not exist'}

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
