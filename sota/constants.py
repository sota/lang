#!/usr/bin/env python2
# -*- coding: utf-8 -*-

__all__ = [
    'BINARY',
    'REPOROOT',
    'SUBS2SHAS',
    'BINDIR',
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
    'PYTHON',
    'RPYTHON',
    'VERSION_H',
    'VERSION_PY',
    'JOBS',
    'RMRF',
    'SOTA_VERSION',
]

from .utils.git import reporoot, subs2shas
from .utils.shell import call, which
from .utils.version import version

BINARY = 'sota-cli'
REPOROOT = reporoot()
SUBS2SHAS = subs2shas()
BINDIR = REPOROOT + '/bin'
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
PYTHON = which('python2')
RPYTHON = REPOROOT + '/repos/pypy/rpython/bin/rpython'
VERSION_H = SOTADIR + '/version.h'
VERSION_PY = SOTADIR + '/version.py'
SOTA_VERSION = version

try:
    JOBS = call('nproc')[1].strip()
except:
    JOBS = 1

try:
    RMRF = which('rmrf')
except:
    RMRF = 'rm -rf'
