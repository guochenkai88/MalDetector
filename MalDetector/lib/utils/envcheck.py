#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

import sys


PYVERSION = sys.version.split()[0]

if PYVERSION >= "3" or PYVERSION < "2.6":
	exit("[CRITICAL] incompatible Python version detected ('%s'). For successfully running apkscan you'll have to use version 2.6 or 2.7 (visit 'http://www.python.org/download/')" % PYVERSION)

extensions = ("bz2", "gzip", "ssl", "sqlite3", "zlib")
try:
	for _ in extensions:
		__import__(_)
except ImportError, ex:
	errMsg = "missing one or more core extensions (%s) " % (", ".join("'%s'" % _ for _ in extensions))
	errMsg += "most probably because current version of Python has been "
	errMsg += "built without appropriate dev packages (e.g. 'libsqlite3-dev')"
	exit(errMsg)