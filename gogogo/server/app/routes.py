import json

import bottle

from gogogo.game import Game, GameError
from gogogo.server.app import app
from gogogo.server.filters import with_game
from gogogo.server.app.players import Player

routes = {
    'root': {
               'GET': [{'/': 'home'}]
            },
    'game': {
               'GET': [{'/game/{game}/': 'Load game'}],
               'POST': [{'/game/create/': 'Create a new game'}],
            },
}


@app.post('/game/:game#[0-9a-f]+#/player/create/', name='game-player-create')
@with_game
def register_player(game):
    required = ('player',)
    try:
        data = json.loads(bottle.request.body.read())
        player = data['player']
    except (ValueError, KeyError):
        raise bottle.HTTPResponse({'message': "JSON seems invalid"}, 400)
    if Player.find(game.name, player=player):
        raise bottle.HTTPResponse({'message': "Game already has a {player}".format(player=player)}, 409)

    player = Player(game.name).update(**data)
    return {'message': '',
            'player': player.uid,
            'game': game.name}

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
    return {'message': '',
            'data': routes}
