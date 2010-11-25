import cherrypy

routes = {
    'root': {
               'GET': [{'/': 'home'}]
            },
    'game': {
               'GET': [{'/game/{game}/': 'Load game'}],
               'POST': [{'/game/new/': 'Create a new game'}],
            },
}


class Index:
    @cherrypy.expose
    def index(self):
        return routes


def run(*args, **kwargs):
    return cherrypy.quickstart(Index())
