import json
import web

app = web.auto_application()

routes = {
    'root': {
               'GET': [{'/': 'home'}]
            },
    'game': {
               'GET': [{'/game/{game}/': 'Load game'}],
               'POST': [{'/game/new/': 'Create a new game'}],
            },
}

class root(app.page):
    path = "/.*"

    def GET(self, *args, **kwargs):
        web.header('Content-Type', 'application/json')
        return json.dumps({'args': args, 'kwargs': kwargs})

#    def GET(self):
#        web.header('Content-Type', 'application/json')
#        return json.dumps(routes)

def run(*args, **kwargs):
    return app.run()
