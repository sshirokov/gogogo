import bottle
from gogogo.game import Game, GameError
from gogogo.server.utils import ParamFilter

def with_game(fn):
    def make_game(game):
        try: return Game(game)
        except GameError: raise bottle.HTTPResponse({'message': 'Game not found'}, 404)
    return ParamFilter(game=make_game)(fn)
