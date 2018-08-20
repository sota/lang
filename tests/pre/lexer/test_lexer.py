#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from pytest import fixture
from sota.lexer import SotaLexer

@fixture
def lexer():
    return SotaLexer()

def test_ctor(lexer):
    assert isinstance(lexer, SotaLexer)

def test_scan(lexer):
    tokens = lexer.scan('0')
    assert tokens
