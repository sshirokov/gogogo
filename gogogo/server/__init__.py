import json

import bottle
from bottle import Bottle, ServerAdapter

from gogogo.game import Game, GameError
from gogogo.server.app import app, routes
from mongrel2 import handler as m2_handler

conn = m2_handler.Connection("54BD6A25-09AC-4964-BE98-F219E8F65C07", "tcp://127.0.0.1:5051",
                             "tcp://127.0.0.1:5050")

class ZMQServer(ServerAdapter):
    def run(self, handler):
        import sys
        while True:
            req = conn.recv()

            if req.is_disconnect():
                continue

            response = handler.handle(req.path, req.headers.get('METHOD'))
            conn.reply_http(req, str(response))

def run(addr='localhost', port=9090, **kwargs):
    bottle.debug(kwargs.pop('debug', False))
    bottle.run(app=app, host=addr, port=port,
               **dict({'reloader': kwargs.pop('reload', False), 
                       'interval': kwargs.pop('reload_interval', 1),
                       'server' : ZMQServer},
                      **kwargs))
