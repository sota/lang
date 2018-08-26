#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from .lexer import SotaLexer

class Sota(object):
    def __init__(self):
        pass

    def run(self, source):
        lexer = SotaLexer()
        if os.path.exists(source):
            with open(source, 'r') as f:
                source = f.read()
        print('source found:')
        print(source)
        tokens = lexer.scan(source)
        for token in tokens:
            print(token.to_str())
        return 0

    def repl(self):
        print('repl time')
        return 0
