import bottle
from gogogo.game import Game, GameError
from gogogo.server.utils import ParamFilter
from gogogo.server.app.players import Player

def with_game(fn):
    def make_game(game, kwargs):
        try: return Game(game)
        except GameError: raise bottle.HTTPResponse({'message': 'Game not found'}, 404)
    return ParamFilter(game=make_game)(fn)

def with_player(fn):
    def make_player(player, kwargs):
        player = Player(kwargs['game'].name, player)
        if player.exists: return player
        else: raise bottle.HTTPResponse({'message': "Player not found"}, 404)
    return ParamFilter(player=make_player)(fn)
