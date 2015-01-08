#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

import os
import sys
import logging
import glob

from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import result
from lib.core.data import paths
from lib.core.data import logger
from lib.core.heartbeat import HeartBeat
from lib.core.storage import Storage
from lib.core.datatype import AttribDict
from lib.controller.plugin import init_plugin
from lib.core.common import send_heartbeat
from lib.parse.configfile import config_file_parser

def _set_conf_attrs():
	"""
	This function set some needed attributes into the configuration
	singleton.
	"""
	debug_msg = "initializing the configuration"
	logger.debug(debug_msg)
	
def _set_kb_attrs(flush_all=True):
	"""
	This function set some needed attributes into the knowledge base
	singleton.
	"""
	debug_msg = "initializing the knowledge base"
	logger.debug(debug_msg)

	kb.apk = AttribDict()
	kb.apk.md5 = None
	kb.apk.file_size = None
	kb.apk.display_perm = []
	kb.apk.providers = []
	kb.apk.receivers = []
	kb.apk.services = []
	kb.apk.activities = []
	kb.apk.actions = []
	kb.apk.manifest = None
	
	if flush_all:
		kb.cache = AttribDict()
		kb.cache.regex = {}
		kb.cache.files = {}
		kb.targets = set()
		kb.heartbeat = None
		kb.storage = None
		kb.plugins = AttribDict()
		kb.plugins.handle = []		

def _set_result_attrs(flush_all=True):
	"""
	This function set some needed attributes into the result
	singleton.
	"""
	debug_msg = "initializing the result"
	logger.debug(debug_msg)
	
	result.plugins = []
		
	
def _set_threads():
	if not isinstance(conf.threads, int) or conf.threads <= 0:
		conf.threads = 1
		
def _set_heartbeat():
	"""
	set heartbeat
	"""
	if conf.monitor:
		debugMsg = "setting the heartbeat connection"
		logger.debug(debugMsg)
		
		kb.heartbeat = HeartBeat(conf.monitor)

def _set_storage():
	"""
	set storage
	"""
	kb.storage = Storage()

def _set_config():
	"""
	load config yaml for init conf
	"""

	debug_msg = "load default config yaml file"
	logger.debug(debug_msg)

	config_file_parser(paths.CONFIG_FILE, override_options=True)

def set_verbosity():
	"""
	This function set the verbosity of apkscan output messages.
	"""

	if conf.verbose is None:
		conf.verbose = 1

	conf.verbose = int(conf.verbose)

	if conf.verbose == 0:
		logger.setLevel(logging.ERROR)
	elif conf.verbose == 1:
		logger.setLevel(logging.INFO)
	elif conf.verbose == 2:
		logger.setLevel(logging.DEBUG)
	elif conf.verbose == 3:
		logger.setLevel(CUSTOM_LOGGING.PAYLOAD)
	elif conf.verbose == 4:
		logger.setLevel(CUSTOM_LOGGING.TRAFFIC_OUT)
	elif conf.verbose >= 5:
		logger.setLevel(CUSTOM_LOGGING.TRAFFIC_IN)

def _merge_options(input_options, override_options):
	"""
	Merge command line options with configuration file and default options.

	@param inputOptions: optparse object with command line options.
	"""
	if input_options.config_file:
		debug_msg = "load config file: %s" %input_options.config_file
		logger.debug(debug_msg)

		config_file_parser(input_options.config_file, override_options=True)

	if hasattr(input_options, "items"):
		input_options_items = input_options.items()
	else:
		input_options_items = input_options.__dict__.items()

	for key, value in input_options_items:
		if key not in conf or value not in (None, False) or override_options:
			if key == 'plugins' and value:
				value = value.split(',')
				value = [i.strip() for i in value]
				for i in value:
					conf[i]['enable'] = True
			else:
				conf[key] = value

	if conf.jad:
		conf.dex2jar = True

def init_options(input_options=AttribDict(), override_options=False):
	_set_conf_attrs()
	_set_kb_attrs()
	_set_result_attrs()
	_set_config()
	_merge_options(input_options, override_options)
	
def init_targets():
	if conf.apk:
		kb.targets.add(conf.apk)
	if conf.apk_path:
		for found in glob.glob(os.path.join(conf.apk_path, "*.apk*")):
			kb.targets.add(found)
			
def flush_env():
	_set_conf_attrs()
	_set_kb_attrs(flush_all=False)
	_set_result_attrs(flush_all=False)
	
def init():
	"""
	Set attributes into both configuration and knowledge base singletons
	based upon command line and configuration file options.
	"""       
	set_verbosity()
	_set_threads()
	_set_heartbeat()
	#_set_storage()
	
	init_targets()
	
	send_heartbeat(start=True)
	
	info_msg = "init plugin script"
	logger.info(info_msg)

	init_plugin()

	info_msg = "loaded %s plugin(s)" %(len(kb.plugins.handle))
	logger.info(info_msg)