import uuid
import os

from gogogo import BoardState

DEFAULTS = dict(
    black="Black",
    white="White",
    x=19,
    y=19,
    data='./data/{name}/'
)

class Game(object):
    "A versioned game"
    def __init__(self, name=None, **options):
        self.name = name or uuid.uuid4().hex
        self.options = dict(DEFAULTS, **options)
        self.options['data'] = self.options['data'].format(name=self.name)

        if not os.path.exists(self.options['data']):
            os.makedirs(self.options['data'])
    def __unicode__(self):
        return "Game: {name} {black} vs {white} on {x}x{y} from {data}".format(
                 name=self.name,
                 **self.options
               )
    __str__=__unicode__

    def __repr__(self):
        return "<%s>" % self
