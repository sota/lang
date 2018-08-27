#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys

sys.dont_write_bytecode = True

from sota.constants import BINDIR
from sota.utils.shell import call
from sota.utils.fmt import fmt, pfmt, dbg

def test_version():
    version = call(fmt('{BINDIR}/sota --version'))[1]
    describe = call('git describe')[1]
    parts = describe.split('-')
    describe = parts[0].replace('v', '') + '.dev{0}+{1}'.format(*parts[1:]) if parts[1:] else ''
    assert version == describe
