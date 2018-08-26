#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from pytest import fixture
from sota import Sota

@fixture
def sota():
    return Sota()

def test_ctor(sota):
    assert isinstance(sota, Sota)

