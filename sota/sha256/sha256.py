#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
hasher: library for hashing source code to store files in unique directory
'''

import os
import sys

from sota.constants import LIBDIR, PYPYDIR, SHA256DIR
sys.path.insert(0, PYPYDIR)

from rpython.rtyper.lltypesystem import rffi
from rpython.translator.tool.cbuild import ExternalCompilationInfo

cli_eci = ExternalCompilationInfo(
    include_dirs=[SHA256DIR],
    includes=['sha256.h'],
    library_dirs=[LIBDIR],
    libraries=['sha256'],
    use_cpp_linker=True)
c_sha256 = rffi.llexternal(
    'sha256',
    [rffi.CCHARP],
    rffi.CCHARP,
    compilation_info=cli_eci)

def sha256(text):
    '''
    sha256
    '''
    return rffi.charp2str(c_sha256(rffi.str2charp(text)))
