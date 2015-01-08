#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

import os
import sys
import glob
import inspect

from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import paths


def _load_plugin(dirname, filename):
	"""
	load plugin script dynamically 
	"""
	ret = None
	debug_msg = "loading plugin script '%s'" % filename[:-3]
	logger.debug(debug_msg)
	#logger.info (debug_msg)

	if dirname not in sys.path:
		sys.path.insert(0, dirname)

	try:
		module = __import__(filename[:-3])
	except ImportError, msg:
		warn_msg = "cannot import plugin script '%s' (%s)" % (filename[:-3], msg)
		logger.warn(warn_msg)
		return ret

	ret = dict(inspect.getmembers(module))

	if "start" not in ret:
		err_msg = "missing function 'start(decoded_path, apk_file)' "
		err_msg += "in plugin script '%s'" % filename
		logger.error(err_msg)
		ret = None
		return ret

	if "init" in ret:
		init_handle = ret["init"]
		try:
			init_handle()
		except Exception,e:
			err_msg = "plugin '%s' init failed. reason:" %filename[:-3]
			err_msg += "\n%s" %e
			logger.error(err_msg)
			ret = None

	return ret

def init_plugin():
	"""
	load plugin script in plugins folder
	"""
	for found in glob.glob(os.path.join(paths.PLUGINS_PATH, "*.py")):
		dirname, filename = os.path.split(found)
		dirname = os.path.abspath(dirname)

		if filename == "__init__.py":
			continue

		_ = _load_plugin(dirname, filename)

		if _ is not None:
			kb.plugins.handle.append(
			    (_["start"], _.get("PLUGIN_INFO", filename[:-3]))
			)

def start_plugin(src, apk):
	"""
	plugin.start()
	"""
	for plugin_handle, plugin_info in kb.plugins.handle:
		info_msg = "start checking '%s' " %plugin_info['name']
		logger.info(info_msg)

		try:
			plugin_handle(src, apk)
		except Exception,e:
			print e

		info_msg = "check '%s'  finished" %plugin_info['name']
		logger.info(info_msg)