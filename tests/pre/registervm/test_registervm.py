#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from pytest import fixture
from sota.registervm import SotaRegisterVM

@fixture
def registervm():
    return SotaRegisterVM()

def test_ctor(registervm):
    assert isinstance(registervm, SotaRegisterVM)

def test_registervm(registervm):
    #bytecode = registervm.execute()
    assert True #FIXME: implement execute to return a bytecode object
