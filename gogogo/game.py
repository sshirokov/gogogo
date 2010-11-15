import uuid
import os

import dulwich.errors
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
        new = False

        self.repo = None
        if not os.path.exists(self.options['data']):
            os.makedirs(self.options['data'])

        try:
            self.repo = Repo(self.options['data'])
        except dulwich.errors.NotGitRepository:
            self.repo = Repo.init_bare(self.options['data'])
            new = True


        self.board = (new and BoardState()) or self.reload_board()

        if new: self.save("New blank board for game: %s" % self.name)

    @property
    def _tree(self):
        try: return self.repo[
                      self.repo.get_object(
                        self.repo.head()
                      ).tree
                    ]
        except KeyError: return Tree()


    def reload_board(self):
        return BoardState.from_json(
            self.repo[
                  [t[2] 
                   for t in self._tree.entries() # [(mode, name, sha)...]
                   if t[1] == 'board.json'].pop()
                 ].data)

    def save(self, message="Forced commit"):
        blob = Blob.from_string(self.board.as_json())
        tree = self._tree
        tree.add(0100644, 'board.json', blob.id)

        [self.repo.object_store.add_object(it)
         for it in (blob, tree)]

        self.repo.do_commit(message, committer="Game %s" % self.name, tree=tree.id)

    def move(self, x, y):
        player = self.board.player_turn()
        if not self.board.game_over and self.board.move(x, y):
            self.save("{player} moved to ({x}, {y})".format(player=player,
                                                            x=x,
                                                            y=y))
            return player
        return None

    def skip(self):
        player = self.board.player_turn()
        if not self.board.game_over:
            self.board.move(None)
            is_or_isnt = (self.board.game_over and "is") or "is NOT"
            self.save("{player} skipped, game {maybe} over".format(player=player,
                                                                   maybe=is_or_isnt))
        return self.board.game_over or self.board.player_turn()

    def __unicode__(self):
        return "Game: {name} {black} vs {white} on {x}x{y} from {data} :: {board}".format(
                 name=self.name,
                 board=self.board,
                 **self.options
               )
    __str__=__unicode__

    def __repr__(self):
        return "<%s>" % self