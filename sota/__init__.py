#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
try:
    from .sota import Sota
except SyntaxError as se:
    #FIXME: this is currently necessary because doit is running in python3
    # and loads some libraries; if this error is thrown on python2, re-raise it
    if sys.version_info.major == 2:
        raise se
