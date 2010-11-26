import json

import bottle
from bottle import Bottle

from gogogo.game import Game, GameError
from gogogo.server.app import app
from gogogo.server.app import routes

def run(addr='localhost', port=9090, **kwargs):
    bottle.debug(kwargs.pop('debug', False))
    bottle.run(app=app, host=addr, port=port,
               **dict({'reloader': kwargs.pop('reload', False), 
                       'interval': kwargs.pop('reload_interval', 1)},
                      **kwargs))
