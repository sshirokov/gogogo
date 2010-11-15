#!/usr/bin/env python
import sys
from gogogo import BoardState
from gogogo.game import Game

def main(self, *args):
    game = Game('default')
    print "Game:", game
    print "-args:", args
    if 'skip' in args: game.skip()
    elif len(args) == 2: game.move(int(args[0]), int(args[1]))
    game.board.dump_board()
    if game.board.game_over:
        print "Game over:", game.board.scores()
    else:
        print "Next:", game.board.player_turn()

if __name__ == "__main__":
    main(sys.argv[0], *sys.argv[1:])
