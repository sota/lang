#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from ruamel import yaml
from doit.task import clean_targets
from sota.utils.git import subs2shas
from sota.utils.shell import call, rglob, globs, which

from sota.utils.version import version
from sota.utils.fmt import *

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

ENVS = ''

dbg(PYTHON)

try:
    J = call('nproc')[1].strip()
except:
    J = 1

try:
    RMRF = which('rmrf')
except:
    RMRF = 'rm -rf'

def task_version():
    '''
    write version.py and version.h
    '''
    templates = {}
    for template in rglob('sota/*.template'):
        filename = template[:-len('.template')]
        contents = open(template).read().format(SOTA_VERSION=version)
        templates[filename] = contents
    def render():
        for filename, contents in templates.items():
            with open(filename, 'w') as f:
                f.write(contents)
    def uptodate():
        for filename, contents in templates.items():
            if os.path.isfile(filename):
                if contents == open(filename).read():
                    continue
            return False
        return True
    return dict(
        actions=[(render,)],
        uptodate=[(uptodate,)],
        targets=list(templates.keys()),
    )


def task_colm():
    '''
    build colm binary for use in build
    '''
    return dict(
        task_dep=[
            'submod:repos/colm'
        ],
        actions=[
            'cd repos/colm && autoreconf -f -i',
            fmt('cd repos/colm && ./configure --prefix={REPOROOT}'),
            'cd repos/colm && make && make install',
        ],
        uptodate=[True],
        targets=[COLM],
        clean=[clean_targets],
    )

def task_ragel():
    '''
    build ragel binary for use in build
    '''
    return dict(
        task_dep=[
            'submod:repos/ragel',
            'colm'
        ],
        actions=[
            'cd repos/ragel && autoreconf -f -i',
            fmt('cd repos/ragel && ./configure --prefix={REPOROOT} --with-colm={REPOROOT} --disable-manual'),
            'cd repos/ragel && make && make install',
        ],
        uptodate=[True],
        targets=[RAGEL],
        clean=[clean_targets],
    )

def task_liblexer():
    '''
    build so libary for use as sota's lexer
    '''
    files = ['sota/lexer/lexer.py'] + rglob('sota/lexer/*.{h,rl,c}')
    return dict(
        file_dep=files,
        task_dep=[
            'ragel',
            'version',
        ],
        actions=[
            fmt('cd sota/lexer && LD_LIBRARY_PATH={REPOROOT}/lib make -j {J} RAGEL={REPOROOT}/{RAGEL}'),
            fmt('install -C -D sota/lexer/liblexer.so {LIBDIR}/liblexer.so'),
        ],
        uptodate=[True],
        targets=[fmt('{LIBDIR}/liblexer.so')],
        clean=[clean_targets],
    )

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
        task_dep=[
            'submod',
            'version',
        ],
        actions=[
            fmt('{ENVS} pylint -j{J} --rcfile {PREDIR}/pylint.rc {SOTADIR} || true'),
        ]
    )

def pre_pytest():
    '''
    run pytest before the build
    '''
    return dict(
        name='pytest',
        task_dep=[
            'submod',
            'version',
            'liblexer'
        ],
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
        task_dep=[
            'submod',
            'version',
            'liblexer',
        ],
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

def task_libcli():
    '''
    build so libary for use as sota's commandline interface
    '''
    files = [DODO] + rglob('src/cli/*.{h,c,cpp}')
    return dict(
        file_dep=files,
        task_dep=[
            'submod:repos/docopt',
        ],
        actions=[
            fmt('cd sota/cli && make -j {J}'),
            fmt('install -C -D sota/cli/libcli.so {LIBDIR}/libcli.so'),
        ],
        uptodate=[True],
        targets=[
            'sota/cli/test',
            fmt('{LIBDIR}/libcli.so'),
        ],
        clean=[clean_targets],
    )

def task_sota():
    '''
    build sota binary using rpython machinery
    '''
    return dict(
        file_dep=[
            DODO,
            fmt('{LIBDIR}/libcli.so'),
            fmt('{LIBDIR}/liblexer.so'),
            fmt('{TARGET}'),
        ] + rglob(fmt('{SOTADIR}/*.py')),
        task_dep=[
            'pre',
            'libcli',
            'liblexer',
        ],
        actions=[
            fmt('mkdir -p {BINDIR}'),
            fmt('{PYTHON} -B {RPYTHON} --no-pdb --output {BINDIR}/sota {TARGET}'),
        ],
        uptodate=[True],
        targets=[fmt('{BINDIR}/sota')],
        clean=[clean_targets],
    )

def post_pytest():
    '''
    run pytest after the build
    '''
    return dict(
        name='pytest',
        task_dep=[
            'sota'
        ],
        actions=[
            fmt('{ENVS} {PYTHON} -m pytest -s -vv {POSTDIR}'),
        ],
    )

def task_post():
    '''
    run tasks after the build: pytest
    '''
    yield post_pytest()

def task_rmcache():
    '''
    recursively delete python cache files
    '''
    return dict(
        actions=[
            'find . -depth -name __pycache__ -type d -exec rm -r "{}" \;',
            'find . -depth -name "*.pyc" -type f -exec rm -r "{}" \;',
        ]
    )

def task_tidy():
    '''
    clean submods and sota/lang repo
    '''
    yield dict(
        name='sota/lang',
        actions=['git clean -xfd'],
    )
    for submod in SUBS2SHAS.keys():
        yield dict(
            name=submod,
            actions=[
                fmt('cd {submod} && git reset --hard HEAD && git clean -xfd')
            ],
        )
