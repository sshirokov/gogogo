#!/usr/bin/env python
import sys
from gogogo import BoardState
from gogogo.game import Game

def main(self, *args):

    game = Game()
    print "Game:", game

if __name__ == "__main__":
    main(sys.argv[0], *sys.argv[:1])
