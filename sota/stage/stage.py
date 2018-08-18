#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
sota.stage
'''

class BaseStage(object):
    '''
    BaseStage
    '''

    def __init__(self):
        '''
        init
        '''
        pass

    def load(self):
        '''
        load
        '''
        raise NotImplementedError
