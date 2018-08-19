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
        BaseStage.__init__(self)

    def parse(self):
        '''
        parse
        '''
        raise NotImplementedError
