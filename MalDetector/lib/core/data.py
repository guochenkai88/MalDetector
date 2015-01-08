#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

from lib.core.datatype import AttribDict
from lib.core.log import LOGGER

# apkscan paths
paths = AttribDict()

# object to store original command line options
cmd_options = AttribDict()

# object to store merged options (command line, configuration file and default options)
merged_options = AttribDict()

# object to share within function and classes command
kb = AttribDict()

# line options and settings
conf = AttribDict()

# object to share within function and classes results
result = AttribDict()

# logger
logger = LOGGER
