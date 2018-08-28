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
            fmt('pylint -j{JOBS} --rcfile {PREDIR}/pylint.rc {SOTADIR} || true'),
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
            'libsha256',
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
            'libsha256',
        ],
        actions=[
            fmt('{PYTHON} -m pytest -s -vv --cov={SOTADIR} {PREDIR}'),
        ],
    )

def pre_mypy():
    '''
    run mypy before the build
    '''
    def package_wanted(directory):
        ignores = [
            'utils',
            '__pycache__',
        ]
        return directory not in ignores and os.path.isdir('sota/'+directory)
    packages = [d for d in os.listdir('sota') if package_wanted(d)]
    return dict(
        name='mypy',
        task_dep=[
            'version',
            'submod',
            'liblexer',
            'libsha256',
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
    #yield pre_pycov()
    yield pre_mypy()

def task_colm():
    '''
    build colm binary for use in build
    '''
    return dict(
        task_dep=[
            fmt('submod:repos/colm'),
        ],
        actions=[
            fmt('cd {COLMDIR} && autoreconf -f -i'),
            fmt('cd {COLMDIR} && ./configure --prefix={REPOROOT}'),
            fmt('cd {COLMDIR} && make && make install'),
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
            fmt('submod:repos/ragel'),
            'colm',
        ],
        actions=[
            fmt('cd {RAGELDIR} && autoreconf -f -i'),
            fmt('cd {RAGELDIR} && ./configure --prefix={REPOROOT} --with-colm={REPOROOT} --disable-manual'),
            fmt('cd {RAGELDIR} && make && make install'),
        ],
        uptodate=[True],
        targets=[RAGEL],
        clean=[clean_targets],
    )

def task_liblexer():
    '''
    build so libary for use as sota's lexer
    '''
    files = [fmt('{LEXERDIR}/lexer.py')] + rglob(LEXERDIR + '/*.{h,rl,c}')
    return dict(
        file_dep=files,
        task_dep=[
            'version',
            'ragel',
        ],
        actions=[
            fmt('cd {LEXERDIR} && LD_LIBRARY_PATH={LIBDIR} make --trace -j {JOBS} RAGEL={RAGEL}'),
            fmt('install -C -D {LEXERDIR}/liblexer.so {LIBDIR}/liblexer.so'),
        ],
        uptodate=[True],
        targets=[
            fmt('{LIBDIR}/liblexer.so'),
            fmt('{LEXERDIR}/lexer.cpp'),
            fmt('{LEXERDIR}/test'),
        ],
        clean=[clean_targets],
    )

def task_libcli():
    '''
    build so libary for use as sota's commandline interface
    '''
    files = [DODO, VERSION_H] + rglob(CLIDIR + '/*.{h,c,cpp}')
    return dict(
        file_dep=files,
        task_dep=[
            'version',
            fmt('submod:repos/docopt'),
        ],
        actions=[
            fmt('cd {CLIDIR} && make --trace -j {JOBS}'),
            fmt('install -C -D {CLIDIR}/libcli.so {LIBDIR}/libcli.so'),
        ],
        uptodate=[True],
        targets=[
            fmt('{CLIDIR}/test'),
            fmt('{LIBDIR}/libcli.so'),
        ],
        clean=[clean_targets],
    )

def task_libsha256():
    '''
    build so library for use as sota's sha256 hashing functionality
    '''
    files = [DODO] + rglob(SHA256DIR + '/*.{h,c,cpp}')
    return dict(
        file_dep=files,
        task_dep=[
            'version',
        ],
        actions=[
            fmt('cd {SHA256DIR} && make --trace -j {JOBS}'),
            fmt('install -C -D {SHA256DIR}/libsha256.so {LIBDIR}/libsha256.so'),
        ],
        uptodate=[True],
        targets=[
            fmt('{SHA256DIR}/test'),
            fmt('{LIBDIR}/libsha256.so'),
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
            fmt('{LIBDIR}/libsha256.so'),
        ] + rglob(fmt('{SOTADIR}/*.py')),
        task_dep=[
            'version',
            'pre',
            'libcli',
            'liblexer',
            'libsha256',
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
    pycache = dict(py2='*.pyc', py3='__pycache__')
    exec_rm = '-exec rm -r "{}" \;'
    for py, cache in pycache.items():
        for dir_ in ('sota', 'tests'):
            yield dict(
                name=py + '-' + dir_,
                actions=[
                    fmt('find {dir_} -depth -name {cache} -type d {exec_rm}'),
                ],
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
