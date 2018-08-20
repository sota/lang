#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from ruamel import yaml
from doit.task import clean_targets
from sota.utils.shell import call, rglob
from sota.utils.fmt import fmt, pfmt, dbg
from sota.constants import *

DODO = 'dodo.py'
COLM = 'bin/colm'
RAGEL = 'bin/ragel'
DOIT_CONFIG = {
    'verbosity': 2,
    'default_tasks': ['post'],
}

def task_version():
    '''
    write version.py and version.h
    '''
    templates = {}
    for template in rglob('sota/*.template'):
        filename = template[:-len('.template')]
        contents = fmt(open(template).read())
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
            'version',
            'ragel',
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
            fmt('pylint -j{J} --rcfile {PREDIR}/pylint.rc {SOTADIR} || true'),
        ]
    )

def pre_pytest():
    '''
    run pytest before the build
    '''
    return dict(
        name='pytest',
        task_dep=[
            'version',
            'submod',
            'liblexer',
        ],
        actions=[
            fmt('echo "{REPOROOT}"'),
            fmt('{PYTHON} -m pytest -s -vv {PREDIR}'),
        ],
    )

def pre_pycov():
    '''
    run pycov before the build
    '''
    return dict(
        name='pycov',
        task_dep=[
            'version',
            'submod',
            'liblexer',
        ],
        actions=[
            fmt('{PYTHON} -m pytest -s -vv --cov={SOTADIR} {PREDIR}'),
        ],
    )

def pre_mypy():
    '''
    run mypy before the build
    '''
    packages = [d for d in os.listdir('sota') if d != 'utils' and os.path.isdir('sota/'+d)]
    return dict(
        name='mypy',
        task_dep=[
            'version',
            'submod',
            'liblexer',
        ],
        actions=[
            'mypy' + ''.join([fmt(' --module sota.{package}') for package in packages]),
        ],
    )

def task_pre():
    '''
    run tasks before the build: pylint, pytest, pycov
    '''
    yield pre_pylint()
    yield pre_pytest()
    yield pre_pycov()
    yield pre_mypy()

def task_libcli():
    '''
    build so libary for use as sota's commandline interface
    '''
    files = [DODO, VERSION_H] + rglob('sota/cli/*.{h,c,cpp}')
    return dict(
        file_dep=files,
        task_dep=[
            'version',
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
            TARGET,
            fmt('{LIBDIR}/libcli.so'),
            fmt('{LIBDIR}/liblexer.so'),
        ] + rglob(fmt('{SOTADIR}/*.py')),
        task_dep=[
            'version',
            'pre',
            'libcli',
            'liblexer',
        ],
        actions=[
            fmt('mkdir -p {BINDIR}'),
            fmt('{PYTHON} -B {RPYTHON} --no-pdb --output {BINDIR}/{BINARY} {TARGET}'),
        ],
        uptodate=[True],
        targets=[fmt('{BINDIR}/{BINARY}')],
        clean=[clean_targets],
    )

def post_pytest():
    '''
    run pytest after the build
    '''
    return dict(
        name='pytest',
        task_dep=[
            'version',
            'sota',
        ],
        actions=[
            fmt('{PYTHON} -m pytest -s -vv {POSTDIR}'),
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
            'find sota/ -depth -name __pycache__ -type d -exec rm -r "{}" \;',
            'find sota/ -depth -name "*.pyc" -type f -exec rm -r "{}" \;',
            'find tests/ -depth -name __pycache__ -type d -exec rm -r "{}" \;',
            'find tests/ -depth -name "*.pyc" -type f -exec rm -r "{}" \;',
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
