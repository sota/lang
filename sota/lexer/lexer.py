#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
sota.lexer
'''

import os
import sys
sys.dont_write_bytecode = True

from sota.constants import LIBDIR, PYPYDIR, LEXERDIR
sys.path.insert(0, PYPYDIR)

from rpython.rtyper.lltypesystem import rffi, lltype
from rpython.translator.tool.cbuild import ExternalCompilationInfo

from .token import Token

CTOKEN = rffi.CStruct(
    'CToken',
    ('kind', rffi.LONG),
    ('start', rffi.LONG),
    ('end', rffi.LONG),
    ('line', rffi.LONG),
    ('pos', rffi.LONG),
    ('skip', rffi.LONG),
    ('debug', rffi.LONG))

CTOKENP = rffi.CArrayPtr(CTOKEN)
CTOKENPP = rffi.CArrayPtr(CTOKENP)

lexer_eci = ExternalCompilationInfo(
    include_dirs=[LEXERDIR],
    includes=['lexer.h'],
    library_dirs=[LIBDIR],
    libraries=['lexer'],
    use_cpp_linker=True)

c_scan = rffi.llexternal( #pylint: disable=invalid-name
    'scan',
    [rffi.CONST_CCHARP, CTOKENPP],
    rffi.LONG,
    compilation_info=lexer_eci)

def deref(obj):
    '''
    deref
    '''
    return obj[0]

def escape(old):
    '''
    escape
    '''
    new = ''
    for char in old:
        if char == '\n':
            new += '\\'
            new += 'n'
        else:
            new += char
    return new

class LookaheadBeyondEndOfTokens(Exception):
    '''
    LookaheadBeyondEndOfTokens
    '''
    pass

class NeedTokensOrSource(Exception):
    '''
    NeedTokensOrSource
    '''
    pass

class SotaLexer(object):
    '''
    SotaLexer
    '''
    def __init__(self):
        '''
        init
        '''
        self.source = None
        self.tokens = []
        self.index = 0

    def scan(self, source):
        '''
        scan
        '''
        self.index = 0
        self.source = source
        del self.tokens[:]
        with lltype.scoped_alloc(CTOKENPP.TO, 1) as ctokenpp:
            csource = rffi.cast(rffi.CONST_CCHARP, rffi.str2charp(source))
            result = c_scan(csource, ctokenpp)
            for i in range(result):
                ctoken  = deref(ctokenpp)[i]
                kind    = rffi.cast(lltype.Signed, ctoken.c_kind)
                start   = rffi.cast(lltype.Signed, ctoken.c_start)
                end     = rffi.cast(lltype.Signed, ctoken.c_end)
                line    = rffi.cast(lltype.Signed, ctoken.c_line)
                pos     = rffi.cast(lltype.Signed, ctoken.c_pos)
                skip    = rffi.cast(lltype.Signed, ctoken.c_skip) != 0
                debug   = rffi.cast(lltype.Signed, ctoken.c_debug)
                assert start >= 0, "start not >= 0"
                assert end >= 0, "end not >= 0"
                value   = self.source[start:end]
                self.tokens.append(Token(kind, value, line, pos, skip, debug))
        return self.tokens

    def lookahead(self, distance, expect=None, skips=False):
        '''
        lookahead
        '''
        index = self.index
        token = None
        while distance:
            if index < len(self.tokens):
                token = self.tokens[index]
            else:
                break
            if token:
                if skips or not token.skip:
                    distance -= 1
            index += 1
        distance = index - self.index
        return token, distance, (token.kind == expect) if token and expect else expect

    def lookahead1(self, expect=None):
        '''
        lookahead1
        '''
        return self.lookahead(1, expect)

    def lookahead2(self, expect=None):
        '''
        lookahead2
        '''
        return self.lookahead(2, expect)

    def consume(self, *expects):
        '''
        consume
        '''
        token, distance, _ = self.lookahead1()
        if not token:
            raise Exception
        if expects:
            for expect in expects:
                if expect == token.name:
                    self.index += distance
                    return token
            return None
        self.index += distance
        return token
