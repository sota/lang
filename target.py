#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
target
'''

import os
import sys

from sota.cli import cli
from sota import Sota

def entry_point(argv):
    '''
    entry_point
    '''
    sota = Sota()
    args = cli.parse(argv)
    exitcode = 0
    if '<source>' in args:
        source = args['<source>']
        exitcode = sota.run(source)
    else:
        exitcode = sota.repl()
    return exitcode

def target(*args):
    '''
    target
    '''
    return entry_point, None

if __name__ == '__main__':
    exitcode = entry_point(sys.argv)
    sys.exit(exitcode)
