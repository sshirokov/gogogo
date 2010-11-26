import json, uuid

import bottle
import mimeparse

from gogogo.game import Game, GameError
from gogogo.server.app import app
from gogogo.server.filters import with_game, with_player
from gogogo.server.app.players import Player

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

@app.post('/game/:game#[0-9a-f]+#/player/:player#[0-9a-f]+#/ping/', name='game-player-ping')
@with_game
@with_player
def ping_player(game, player):
    return {'message': '',
            'player': player.uid,
            'ok': True}

@app.post('/game/:game#[0-9a-f]+#/player/:player#[0-9a-f]+#/skip/', name='game-player-skip')
@with_game
@with_player
def player_skip(game, player):
    if game.who() != player.info['player']:
        raise bottle.HTTPResponse({'message': 'Not your turn', 'status': False}, 409)
    return {'message': '',
            'status': game.skip(),
            'data': game.board.take_snapshot()}

@app.post('/game/:game#[0-9a-f]+#/player/:player#[0-9a-f]+#/move/', name='game-player-move')
@with_game
@with_player
def player_move(game, player):
    if game.who() != player.info['player']:
        raise bottle.HTTPResponse({'message': 'Not your turn', 'status': False}, 409)
    try:
        data = json.loads(bottle.request.body.read())
        x = data['x']
        y = data['y']
    except (ValueError, KeyError):
        raise bottle.HTTPResponse({'message': "JSON seems invalid"}, 400)
    return {'message': '',
            'status': game.move(x, y) and True or False,
            'data': game.board.take_snapshot()}


@app.get('/game/:game#[0-9a-f]+#/branch/', name='game-branch-index')
@with_game
def branches(game):
    return {'message': '',
            'current': game.branch,
            'branches': game.branches()}

@app.post('/game/:game#[0-9a-f]+#/branch/change/', name='game-branch-switch')
@with_game
def change_branch(game):
    try:
        data = json.loads(bottle.request.body.read())
        name = data['name']
        return {'message': '',
                'status': game.set_branch(name)}
    except (ValueError, KeyError):
        raise bottle.HTTPResponse({'message': "JSON seems invalid"}, 400)
    except GameError:
        raise bottle.HTTPResponse({'message': "Could not change branch"}, 404)


@app.post('/game/:game#[0-9a-f]+#/branch/create/', name='game-branch-create')
@with_game
def create_branch(game):
    try:
        data = json.loads(bottle.request.body.read())
        name = data.get('name', uuid.uuid4().hex)
        back = data.get('back', 0)
        return {'message': '',
                'status': game.make_branch(name, back)}
    except (ValueError, KeyError):
        raise bottle.HTTPResponse({'message': "JSON seems invalid"}, 400)
    except GameError:
        raise bottle.HTTPResponse({'message': "Could not create branch"}, 409)

@app.get('/game/:game#[0-9a-f]+#/branch/:branch#[\w_-]+#/', name='game-branch')
@with_game
def game_branch(game, branch):
    try: board = game.get_board(branch)
    except GameError: raise bottle.HTTPResponse({'message': "Cannot load branch"}, 404)

    return {'message': '',
            'turn': board.player_turn(),
            'over': board.game_over,
            'data': board.take_snapshot()}

@app.get('/game/:game#[0-9a-f]+#/', name='game-index')
@with_game
def game(game):
    return {'message': '',
            'turn': game.who(),
            'over': game.board.game_over,
            'data': game.board.take_snapshot()}

@app.post('/game/create/', name='game-create')
def new_game():
    game = Game(create=True)
    bottle.redirect(app.get_url('game-index', game=game.name))

@app.get('/', name='index')
def index():
    use = mimeparse.best_match(['application/json', 'text/html'], bottle.request.header.get('accept'))
    return {'message': '',
            'accept': bottle.request.header.get('accept'),
            'use': use}
