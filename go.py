#!/usr/bin/env python
import sys
from gogogo import BoardState

def main(self, *args):
    board = BoardState('Black', 'White')
    print "Board: ", board
    board._set(5, 5, "Black")
    board._set(10, 4, "White")
    board.dump_board()

if __name__ == "__main__":
    main(sys.argv[0], *sys.argv[:1])
