#!/usr/bin/env python
import sys
from gogogo import BoardState

def main(self, *args):
    board = BoardState('Black', 'White')
    print "Board: ", board
    board.move(5, 5)
    board.move(10, 4)
    board.dump_board()
    print board.as_json()

if __name__ == "__main__":
    main(sys.argv[0], *sys.argv[:1])
