#!/usr/bin/env python2
# -*- coding: utf-8 -*-

__all__ = [
    'BINARY',
    'REPOROOT',
    'DODO',
    'SUBS2SHAS',
    'BINDIR',
    'COLM',
    'RAGEL',
    'LIBDIR',
    'SOTADIR',
    'CLIDIR',
    'LEXERDIR',
    'SHA256DIR',
    'PREDIR',
    'POSTDIR',
    'PYPYDIR',
    'COLMDIR',
    'RAGELDIR',
    'DOCOPTDIR',
    'TARGET',
    'RPYTHON',
    'VERSION_H',
    'VERSION_PY',
    'JOBS',
    'RMRF',
    'PYTHON',
    'SOTA_VERSION',
]

from .utils.git import reporoot, subs2shas
from .utils.shell import call, which
from .utils.version import version

BINARY = 'sota-cli'
REPOROOT = reporoot()
DODO = REPOROOT + '/dodo.py'
SUBS2SHAS = subs2shas()
BINDIR = REPOROOT + '/bin'
COLM = BINDIR + '/colm'
RAGEL = BINDIR + '/ragel'
LIBDIR = REPOROOT + '/lib'
SOTADIR = REPOROOT + '/sota'
CLIDIR = SOTADIR + '/cli'
LEXERDIR = SOTADIR + '/lexer'
SHA256DIR = SOTADIR + '/sha256'
PREDIR = REPOROOT + '/tests/pre'
POSTDIR = REPOROOT + '/tests/post'
PYPYDIR = REPOROOT + '/repos/pypy'
COLMDIR = REPOROOT + '/repos/colm'
RAGELDIR = REPOROOT + '/repos/ragel'
DOCOPTDIR = REPOROOT + '/repos/docopt'
TARGET = REPOROOT + '/target.py'
RPYTHON = REPOROOT + '/repos/pypy/rpython/bin/rpython'
VERSION_H = SOTADIR + '/version.h'
VERSION_PY = SOTADIR + '/version.py'
PYTHON = which('python2')
SOTA_VERSION = version

try:
    JOBS = call('nproc')[1].strip()
except:
    JOBS = 1

try:
    RMRF = which('rmrf')
except:
    RMRF = 'rm -rf'
