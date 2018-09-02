#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from .lexer import SotaLexer
from .sha256 import sha256

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
        print
        sourcehash = sha256(source)
        print('source hash:')
        print(sourcehash)
        print
        tokens = lexer.scan(source)
        for token in tokens:
            print(token.to_str())
        return 0

    def repl(self):
        print('repl time')
        return 0
