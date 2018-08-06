#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from ruamel import yaml
from doit.task import clean_targets
from sota.utils.fmt import fmt
from sota.utils.git import subs2shas
from sota.utils.shell import call, rglob, globs, which
from sota.utils.version import SotaVersionWriter

REPOROOT = os.path.dirname(os.path.abspath(__file__))
PREDIR = fmt('{REPOROOT}/tests')
POSTDIR = fmt('{REPOROOT}/tests/post')
BINDIR = fmt('{REPOROOT}/bin')
LIBDIR = fmt('{REPOROOT}/lib')
SOTADIR = fmt('{REPOROOT}/sota')

DODO = 'dodo.py'
COLM = 'bin/colm'
RAGEL = 'bin/ragel'
PYTHON = which('python2')
RPYTHON = 'repos/pypy/rpython/bin/rpython'
TARGET = 'target.py'
VERSION_JSON = 'sota/version.json'
VERSION_YML = 'sota/version.yml'
SUBS2SHAS = subs2shas()

DOIT_CONFIG = {
    'verbosity': 2,
    'default_tasks': ['post'],
}

ENVS = ' '.join([
    'PYTHONPATH=.:sota:sota/pypy:$PYTHONPATH',
])

try:
    J = call('nproc')[1].strip()
except:
    J = 1

try:
    SOTA_VERSION = open('VERSION').read().strip()
except:
    try:
        SOTA_VERSION = call('git describe')[1].strip()
    except:
        SOTA_VERSION = 'UNKNOWN'

def task_submod():
    '''
    run ensure git submodules are up to date
    '''
    SYMS = [
        '+',
        '-',
    ]
    for submod, sha1hash in SUBS2SHAS.items():
        yield dict(
            name=submod,
            actions=[
                fmt('git submodule update --init {submod}')
            ],
            uptodate=[all(map(lambda sym: not sha1hash.startswith(sym), SYMS))],
        )

def pre_pylint():
    '''
    run pylint before the build
    '''
    return dict(
        name='pylint',
#        task_dep=[
#            'submod',
#            'version:src/sota/version.py',
#        ],
        actions=[
            fmt('{ENVS} pylint -j{J} --rcfile {PREDIR}/pylint.rc {SOTADIR}'),
        ]
    )

def pre_pytest():
    '''
    run pytest before the build
    '''
    return dict(
        name='pytest',
#        task_dep=[
#            'version:src/sota/version.py',
#            'liblexer'
#        ],
        actions=[
            fmt('{ENVS} {PYTHON} -m pytest -s -vv {PREDIR}'),
        ],
    )

def pre_pycov():
    '''
    run pycov before the build
    '''
    return dict(
        name='pycov',
#        task_dep=[
#            'submod',
#            'version:src/sota/version.py',
#            'liblexer',
#        ],
        actions=[
            fmt('{ENVS} {PYTHON} -m pytest -s -vv --cov={SOTADIR} {PREDIR}'),
        ]
    )

def task_pre():
    '''
    run tasks before the build: pylint, pytest, pycov
    '''
    yield pre_pylint()
    yield pre_pytest()
    yield pre_pycov()

