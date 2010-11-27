import bottle

class TornadoServer(bottle.ServerAdapter):
    """
    Jacked from bottle.py and added the ability to specify a host"
    """
    def run(self, handler): # pragma: no cover
        import tornado.wsgi
        import tornado.httpserver
        import tornado.ioloop
        container = tornado.wsgi.WSGIContainer(handler)
        server = tornado.httpserver.HTTPServer(container)
        server.listen(self.port, self.host)
        tornado.ioloop.IOLoop.instance().start()
