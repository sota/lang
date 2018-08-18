#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
sota.lexer
'''

from sota.stage import BaseStage

class SotaLexer(BaseStage):
    '''
    SotaLexer
    '''

    def __init__(self):
        '''
        init
        '''
        super(SotaLexer, self).__init__()

    def scan(self, *args, **kwargs):
        '''
        scan
        '''
        raise NotImplementedError
