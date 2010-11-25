#!/usr/bin/env python
import sys
from gogogo import BoardState
from gogogo.game import Game
from optparse import OptionParser

def options_arguments_and_parser():
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port", default=9090,
                      type="int",
                      help="PORT to listen on [default: %default]", metavar="PORT")
    parser.add_option("-a", "--addr", dest="addr", default='127.0.0.1',
                      type="string",
                      help="ADDR to listen on [default: %default]", metavar="ADDR")
    parser.add_option('-d', '--debug', dest="debug", default=False,
                      action="store_true",
                      help="Enable debug mode.")
    parser.add_option('-r', '--reload', dest="reload", default=False,
                      action="store_true",
                      help="Enable autoreloader")
    (options, args) = parser.parse_args()
    return options.__dict__, args, parser

def main(*args, **options):
    print "main:", args, options
    from gogogo import server
    return server.run(options.pop('addr'), options.pop('port'), **options)

def fail(code=None, msg=None, e=None):
    print "CATASTROFIC ERROR!"

    if msg is not None: sys.stderr.write("Error: {0}\n".format(msg))
    if e is not None: sys.stderr.write("Error: {0}\n".format(str(e)))

    if code is not None: exit(code)

if __name__ == "__main__":
    options, args, parser = options_arguments_and_parser()

    main(*args, **options)
