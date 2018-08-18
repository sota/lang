#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
sota.parser
'''

from sota.stage import BaseStage

class SotaParser(BaseStage):
    '''
    SotaParser
    '''

    def __init__(self):
        '''
        init
        '''
        super(SotaParser, self).__init__()

    def parse(self):
        '''
        parse
        '''
        raise NotImplementedError
