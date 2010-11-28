from gogogo.util import make_consuming_chain

class multiroute(object):
    def __init__(self, *routes, **options):
        self.options = dict({}, **options)
        self.routes = routes

    def __call__(self, fn):
        create_chain = lambda routes: make_consuming_chain(*routes[::-1])
        [create_chain(routes)(fn)
         for routes in self.routes]
        return fn

