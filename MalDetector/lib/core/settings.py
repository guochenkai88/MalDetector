#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

import os
import re
import subprocess
import string
import sys

VERSION = "1.0-dev"
VERSION_STRING = "apkscan/%s" % (VERSION)
DESCRIPTION = "automatic apk file analysis tool"

# String representation for NULL value
NULL = "NULL"

# String representation for blank ('') value
BLANK = "<blank>"

# Encoding used for Unicode data
UNICODE_ENCODING = "utf8"

# IP address of the localhost
LOCALHOST = "127.0.0.1"

# Regular expression used for recognition of IP addresses
IP_ADDRESS_REGEX = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"

# Format used for representing invalid unicode characters
INVALID_UNICODE_CHAR_FORMAT = r"\?%02x"

# System variables
IS_WIN = subprocess.mswindows

# The name of the operating system dependent module imported. The following names have currently been registered: 'posix', 'nt', 'mac', 'os2', 'ce', 'java', 'riscos'
PLATFORM = os.name
PYVERSION = sys.version.split()[0]
