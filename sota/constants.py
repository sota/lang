#!/usr/bin/env python2
# -*- coding: utf-8 -*-

__all__ = [
    'BINARY',
    'REPOROOT',
    'SUBS2SHAS',
    'VERSION',
    'SOTADIR',
    'BINDIR',
    'LIBDIR',
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
    'J',
    'RMRF',
]

from .utils.git import reporoot, subs2shas
from .utils.shell import which
from .utils.version import version

BINARY = 'sota-cli'
REPOROOT = reporoot()
SUBS2SHAS = subs2shas()
VERSION = version
SOTADIR = REPOROOT + '/sota'
BINDIR = REPOROOT + '/bin'
LIBDIR = REPOROOT + '/lib'
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

try:
    J = call('nproc')[1].strip()
except:
    J = 1

try:
    RMRF = which('rmrf')
except:
    RMRF = 'rm -rf'
