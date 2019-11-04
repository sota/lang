#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from ruamel import yaml
from doit.task import clean_targets

from sota.utils.shell import call, rglob
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
        contents = open(template).read()
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
                f'git submodule update --init {submod}'
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
            'pylint -j{JOBS} --rcfile {PREDIR}/pylint.rc {SOTADIR} || true',
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
            f'echo "{REPOROOT}"',
            f'{PYTHON} -m pytest -s -vv {PREDIR}',
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
            f'{PYTHON} -m pytest -s -vv --cov={SOTADIR} {PREDIR}',
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
            'mypy' + ''.join([f' --module sota.{package}' for package in packages]),
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
            f'submod:repos/colm',
        ],
        actions=[
            f'cd {COLMDIR} && autoreconf -f -i',
            f'cd {COLMDIR} && ./configure --prefix={REPOROOT}',
            f'cd {COLMDIR} && make && make install',
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
            'colm',
        ],
        actions=[
            f'cd {RAGELDIR} && autoreconf -f -i',
            f'cd {RAGELDIR} && ./configure --prefix={REPOROOT} --with-colm={REPOROOT} --disable-manual',
            f'cd {RAGELDIR} && make && make install',
        ],
        uptodate=[True],
        targets=[RAGEL],
        clean=[clean_targets],
    )

def task_liblexer():
    '''
    build so libary for use as sota's lexer
    '''
    files = [f'{LEXERDIR}/lexer.py'] + rglob(LEXERDIR + '/*.{h,rl,c}')
    return dict(
        file_dep=files,
        task_dep=[
            'version',
            'ragel',
        ],
        actions=[
            f'cd {LEXERDIR} && LD_LIBRARY_PATH={LIBDIR} make --trace -j {JOBS} RAGEL={RAGEL}',
            f'install -C -D {LEXERDIR}/liblexer.so {LIBDIR}/liblexer.so',
        ],
        uptodate=[True],
        targets=[
            f'{LIBDIR}/liblexer.so',
            f'{LEXERDIR}/lexer.cpp',
            f'{LEXERDIR}/test',
        ],
        clean=[clean_targets],
    )

def task_graph():
    '''
    create Graphviz PNGs
    '''
    for machine in ('body', 'string', 'commenter'):
        yield dict(
            name=machine,
            file_dep=[
                f'{LEXERDIR}/lexer.rl',
            ],
            task_dep=[
                'liblexer',
            ],
            actions=[
                f'cd {LEXERDIR} && {RAGEL} lexer.rl -V -M {machine} -o {machine}.dot',
                f'cd {LEXERDIR} && dot -Tpng {machine}.dot -o {machine}.png',
            ],
            targets=[
                f'{LEXERDIR}/{machine}.dot',
                f'{LEXERDIR}/{machine}.png',
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
            'submod:repos/docopt',
        ],
        actions=[
            f'cd {CLIDIR} && make --trace -j {JOBS}',
            f'install -C -D {CLIDIR}/libcli.so {LIBDIR}/libcli.so',
        ],
        uptodate=[True],
        targets=[
            f'{CLIDIR}/test',
            f'{LIBDIR}/libcli.so',
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
            f'cd {SHA256DIR} && make --trace -j {JOBS}',
            f'install -C -D {SHA256DIR}/libsha256.so {LIBDIR}/libsha256.so',
        ],
        uptodate=[True],
        targets=[
            f'{SHA256DIR}/test',
            f'{LIBDIR}/libsha256.so',
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
            f'{LIBDIR}/libcli.so',
            f'{LIBDIR}/liblexer.so',
            f'{LIBDIR}/libsha256.so',
        ] + rglob(f'{SOTADIR}/*.py'),
        task_dep=[
            'version',
            'pre',
            'libcli',
            'liblexer',
            'libsha256',
        ],
        actions=[
            f'mkdir -p {BINDIR}',
            f'{PYTHON} -B {RPYTHON} --no-pdb --output {BINDIR}/{BINARY} {TARGET}',
        ],
        uptodate=[True],
        targets=[f'{BINDIR}/{BINARY}'],
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
            f'{PYTHON} -m pytest -s -vv {POSTDIR}',
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
                    f'find {dir_} -depth -name {cache} -type d {exec_rm}',
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
                f'cd {submod} && git reset --hard HEAD && git clean -xfd'
            ],
        )
