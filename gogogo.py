#!/usr/bin/env python
import sys

class BoardState(object):
    def __init__(self, *players, **options):
        '''
        Call with __init__(list, of players, width=n, height=m...)
        '''
        options = dict({'width': 19,
                        'height': 19,
                        'players': players,
                        },
                       **options)
        self.moves = options.pop('moves', {})
        if not self.moves:
            [self.moves.update({name: []}) for name in options['players']]
        [setattr(self, k, v) for (k, v) in options.items()]

    def __str__(self):
        return u"<Board: (%d, %d) :: (%s) Moves: %d>" % (self.width, self.height, " vs ".join(self.players), sum([len(m) for (n, m) in self.moves.items()]))
    __unicode__ = __str__

def main(self, *args):
    board = BoardState('Black', 'White')
    print "Board: ", board

if __name__ == "__main__":
    main(sys.argv[0], *sys.argv[:1])

