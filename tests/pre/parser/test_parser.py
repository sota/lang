#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from pytest import fixture
from sota.parser import SotaParser

@fixture
def parser():
    return SotaParser()

def test_ctor(parser):
    assert isinstance(parser, SotaParser)

def test_parse(parser):
    #tree = parser.parse()
    assert True #FIXME: implement parse to return a tree object
