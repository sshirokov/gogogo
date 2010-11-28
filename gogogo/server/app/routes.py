import json, uuid

import bottle
import mimeparse

from gogogo.game import Game, GameError
from gogogo.server.app import app
from gogogo.server.filters import with_game, with_player
from gogogo.server.app.players import Player

def make_consuming_chain(*functions):
    '''
    Return a function that will call functions in sequence, passing the return down the chain of functions
    '''
    return reduce(lambda acc, f: lambda *args, **kwargs: f(acc(*args, **kwargs)), functions)

class multiroute(object):
    def __init__(self, *routes, **options):
        self.options = dict({}, **options)
        self.routes = routes

    def __call__(self, fn):
        create_chain = lambda routes: make_consuming_chain(*routes[::-1])
        [create_chain(routes)(fn)
         for routes in self.routes]
        return fn

#Small helpers
@multiroute(
    [
        app.post('/game/:game#[0-9a-f]+#/ping/', name='game-anon-ping'),
        with_game
    ],
    [
        app.post('/game/:game#[0-9a-f]+#/player/:player#[0-9a-f]+#/ping/', name='game-player-ping'),
        with_game,
        with_player
    ]
)
def ping_reply(game, player=None):
    return dict({'message': '',
                 'state': Player.game_state(game.name),
                 'gamesig': game.signature(),
                 'ok': True},
                **(player and {'player': player.uid} or {}))

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

@app.post('/game/:game#[0-9a-f]+#/player/:player#[0-9a-f]+#/skip/', name='game-player-skip')
@with_game
@with_player
def player_skip(game, player):
    if game.who() != player.info['player']:
        raise bottle.HTTPResponse({'message': 'Not your turn', 'status': False}, 409)
    return {'message': '',
            'status': game.skip(),
            'gamesig': game.signature()}

@app.post("/game/:game#[0-9a-f]+#/player/:player#[0-9a-f]+#/boot-other/", name="game-player-boot")
@with_game
@with_player
def boot_other(game, player):
    return {'message': '',
            'count': len([p.delete()
                          for p in Player.find(game.name, exclude={'uid': player.uid})])}

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
            'gamesig': game.signature()}

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
        if not Player(game.name, data['player']).exists:
            raise GameError("Need player to create branch")
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
        back = int(data.get('back', 0))
        if not Player(game.name, data['player']).exists:
            raise GameError("Need player to create branch")
        return {'message': '',
                'status': game.make_branch(name, back)}
    except (ValueError, TypeError, KeyError):
        raise bottle.HTTPResponse({'message': "JSON seems invalid"}, 400)
    except GameError:
        raise bottle.HTTPResponse({'message': "Could not create branch"}, 409)

@app.get('/game/:game#[0-9a-f]+#/branch/:branch#[\w_-]+#/', name='game-branch')
@with_game
def game_branch(game, branch):
    try: board = game.get_board(branch)
    except GameError: raise bottle.HTTPResponse({'message': "Cannot load branch"}, 404)

    return {'message': '',
            'name': game.name,
            'turn': board.player_turn(),
            'over': board.game_over,
            'gamesig': game.signature(branch),
            'scores': game.scores(),
            'data': board.take_snapshot()}

@app.get('/game/:game#[0-9a-f]+#/', name='game-index')
@with_game
def game(game):
    return {'message': '',
            'name': game.name,
            'turn': game.who(),
            'over': game.board.game_over,
            'state': Player.game_state(game.name),
            'gamesig': game.signature(),
            'scores': game.scores(),
            'data': game.board.take_snapshot()}

@app.post('/game/create/', name='game-create')
def new_game():
    game = Game(create=True)
    url = app.get_url('game-index', game=game.name)
    bottle.response.headers['location'] = url
    return bottle.HTTPResponse({'message': '', 'game': game.name}, 201)

@app.get('/', name='index')
def index():
    use = mimeparse.best_match(['application/json', 'text/html'], bottle.request.header.get('accept'))
    if use == 'application/json':
        return {'message': '',
                'accept': bottle.request.header.get('accept'),
                'use': use}
    else:
        return bottle.static_file('index.html', root=app.config['media_root'])

@app.get('/static/:path#.+#', name='static')
def static(path):
    import os
    return bottle.static_file(path, root=os.path.join(app.config['media_root'], 'static'))
