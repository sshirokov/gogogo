#!/usr/bin/env python
import sys

class BoardError(Exception): pass
class HistoryInvalid(BoardError): pass

class BoardState(object):
    def __init__(self, *players, **options):
        '''
        Call with __init__(list, of players, width=n, height=m...)
        '''
        options = dict({'width': 19,
                        'height': 19,
                        'players': players,
                        'moves': [],
                        'positions': [],
                        },
                       **options)
        [setattr(self, k, v) for (k, v) in options.items()]
        if not self.validate(): raise HistoryInvalid()

    def validate(self):
        return True

    def __str__(self):
        return u"<Board: (%d, %d) :: (%s) Moves: %d>" % (self.width, self.height, " vs ".join(self.players), len(self.moves))
    __unicode__ = __str__


