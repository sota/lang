#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
sota.cli
'''

import os
import sys

from sota.constants import LIBDIR, SOTADIR, PYPYDIR
sys.path.insert(0, PYPYDIR)

from rpython.rtyper.lltypesystem import rffi
from rpython.translator.tool.cbuild import ExternalCompilationInfo

lib_dir = LIBDIR
cli_dir = SOTADIR + '/cli'
cli_eci = ExternalCompilationInfo(
    include_dirs=[cli_dir],
    includes=['cli.h'],
    library_dirs=[lib_dir],
    libraries=['cli'],
    use_cpp_linker=True)
CliToken = rffi.CStruct(
    'CliToken',
    ('name', rffi.CCHARP),
    ('value', rffi.CCHARP))
CliTokenPtr = rffi.CArrayPtr(CliToken)
CliTokensPtr = rffi.CStructPtr(
    'CliTokens',
    ('count', rffi.LONG),
    ('tokens', CliTokenPtr))
c_parse = rffi.llexternal(
    'parse',
    [rffi.LONG, rffi.CCHARPP],
    CliTokensPtr,
    compilation_info=cli_eci)
c_clean = rffi.llexternal(
    'clean',
    [CliTokensPtr],
    rffi.LONG,
    compilation_info=cli_eci)

#class CliParseError(Exception):
#    '''
#    CliParseError
#    '''
#    def __init__(self, result):
#        '''
#        init
#        '''
#        msg = 'CliParseError result =' + str(result)
#        super(CliParseError, self).__init__(msg)

def parse(argv):
    '''
    parse
    '''
    args = {}
    tokens = c_parse(len(argv), rffi.liststr2charpp(argv))
    for i in range(tokens.c_count):
        token = tokens.c_tokens[i]
        name = rffi.charp2str(token.c_name)
        value = rffi.charp2str(token.c_value)
        args[name] = value
    result = c_clean(tokens)
    if result:
        print('ERRROR: result =', result)
        #raise CliParseError(result)
    return args
