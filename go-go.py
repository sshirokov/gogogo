#!/usr/bin/env python
import sys
from gogogo import BoardState
from gogogo.game import Game

def options_arguments_and_parser():
    parser = OptionParser()
    parser.add_option("-n", "--name", dest="name",
                  help="NAME of a game", metavar="NAME")
    (options, args) = parser.parse_args()
    return options, args, parser

def main(name, x=None, y=None, **options):
    game = Game(name)
    print "Game:", game
    if 'skip' in args: game.skip()
    elif len(args) == 2: game.move(int(args[0]), int(args[1]))
    game.board.dump_board()
    if game.board.game_over:
        print "Game over:", game.scores()
        print "Winner:", game.winner() or "Tie"
    else:
        print "Next:", game.who()

if __name__ == "__main__":
    main(sys.argv[0], *sys.argv[1:])
