#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
target
'''

import os
import sys

from sota.cli import cli
from sota.lexer import SotaLexer

def entry_point(argv):
    '''
    entry_point
    '''
    args = cli.parse(argv)
    if '<source>' in args:
        source = args['<source>']
        lexer = SotaLexer()
        if os.path.exists(source):
            with open(source, 'r') as f:
                source = f.read()
        print('source found:')
        print(source)
        tokens = lexer.scan(source)
        for token in tokens:
            print(token.to_str())
    else:
        print('repl time')
    return 0

def target(*args):
    '''
    target
    '''
    return entry_point, None

if __name__ == '__main__':
    exitcode = entry_point(sys.argv)
    sys.exit(exitcode)
