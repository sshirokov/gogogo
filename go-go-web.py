#!/usr/bin/env python
import sys
from gogogo import BoardState
from gogogo.game import Game
from optparse import OptionParser

def options_arguments_and_parser():
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port",
                      type='int',
                      default=9090,
                      help="PORT to serve on", metavar="PORT")

    (options, args) = parser.parse_args()
    return options.__dict__, args, parser

def main(*args, **options):
    print "main:", args, options

def fail(code=None, msg=None, e=None):
    print "CATASTROFIC ERROR!"

    if msg is not None: sys.stderr.write("Error: {0}\n".format(msg))
    if e is not None: sys.stderr.write("Error: {0}\n".format(str(e)))

    if code is not None: exit(code)

if __name__ == "__main__":
    options, args, parser = options_arguments_and_parser()

    try: main(*args, **options)
    except Exception, e:
        parser.error("Error in main: {0}".format(str(e)))
        fail(1, "main() failed", e)
