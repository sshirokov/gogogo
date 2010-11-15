import uuid
import os

from dulwich.repo import Repo
from dulwich.objects import Tree, Blob

from gogogo import BoardState

DEFAULTS = dict(
    black="Black",
    white="White",
    x=19,
    y=19,
    data=os.path.join('.', 'data', '{name}')
)

class Game(object):
    "A versioned game"
    def __init__(self, name=None, **options):
        self.name = name or uuid.uuid4().hex
        self.options = dict(DEFAULTS, **options)
        self.options['data'] = self.options['data'].format(name=self.name)
        self.new = False

        if not os.path.exists(self.options['data']):
            os.makedirs(self.options['data'])
            self.repo = Repo.init_bare(self.options['data'])
            self.new = True
        else:
            self.repo = Repo(self.options['data'])

        self.board = self.reload_board()

    def reload_board(self):
        pass

    def save(self, message="Forced commit"):
        pass

    def __unicode__(self):
        return "Game: {name} {black} vs {white} on {x}x{y} from {data}".format(
                 name=self.name,
                 **self.options
               )
    __str__=__unicode__

    def __repr__(self):
        return "<%s>" % self
