#!/usr/bin/env python
#coding:utf-8
# Author:  hysia
# Purpose: 
# Created: 09/17/2013

import os
import signal
import time
from subprocess import PIPE
from lib.core.settings import IS_WIN

from lib.core.data import paths
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.common import check_file
from lib.core.common import md5_sum
from lib.core.common import get_apk_md5
from lib.core.common import get_unicode
from lib.core.common import unzip
from lib.core.common import is_dir_empty
from lib.core.common import run_wait
from lib.core.common import kill_child_processes
from lib.core.exception import ApkscanTimeoutException
from lib.core.subprocessng import Popen
from lib.core.subprocessng import send_all
from lib.core.subprocessng import recv_some


########################################################################
class AndroidVersionMap(object):
	
	""""""

	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		self.map_data = (
		    ('1','Android 1.0'),
		    ('2','Android 1.1'),
		    ('3','Android 1.5'),
		    ('4','Android 1.6'),
		    ('5','Android 2.0'),
		    ('6','Android 2.0.1'),
		    ('7','Android 2.1'),
		    ('8','Android 2.2'),
		    ('9','Android 2.3'),
		    ('10','Android 2.3.3'),
		    ('11','Android 3.0'),
		    ('12','Android 3.1'),
		    ('13','Android 3.2'),
		    ('14','Android 4.0'),
		    ('15','Android 4.0.3'),
		    ('16','Android 4.1'),
		    ('17','Android 4.2'),
		    ('18','Android 4.3'),		    
		    )
		
	def get_version(self, value):
		ret = ''
		for k, v in self.map_data:
			if value == k:
				ret = v
				break
		return ret

########################################################################

def aapt(src, async=False):
	"""
	get infomation from apk file
	"""
	ret = ""
	check_file(src)
	
	info_msg = "analysis apk file '%s'" %src
	logger.info(info_msg)	
	
	try:
		aapt_postfix = ".exe" if IS_WIN else ""
		aapt_bin = os.path.join(conf.apktool_path,'aapt' + aapt_postfix)
		if not os.path.exists(aapt_bin):
			err_msg = "aapt file is not exists in path[%s]" %conf.apktool_path
			logger.error(err_msg)
			return ret
		
		cmd = '%s dump badging "%s"' %(aapt_bin, src)
		process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE, close_fds=False)
		out, err = process.communicate()
		if not async:
			process.wait()
		ret = out
		time.sleep(1)
		return ret
	except Exception,e:
		print e
	
	return ret	

def aapt_permissions(src, async=False):
	"""
	get infomation from apk file
	"""
	ret = ""
	check_file(src)
	
	info_msg = "analysis apk file '%s'" %src
	logger.info(info_msg)	
	
	try:
		aapt_postfix = ".exe" if IS_WIN else ""
		aapt_bin = os.path.join(conf.apktool_path,'aapt' + aapt_postfix)
		if not os.path.exists(aapt_bin):
			err_msg = "aapt file is not exists in path[%s]" %conf.apktool_path
			logger.error(err_msg)
			return ret
		
		cmd = '%s dump permissions "%s"' %(aapt_bin, src)
		process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE, close_fds=False)
		out, err = process.communicate()
		if not async:
			process.wait()
		ret = out
		time.sleep(1)
		return ret
	except Exception,e:
		print e
	
	return ret

def apktool(src, dest=None, flush=False, async=False):
	"""
	decode apk file
	"""
	ret = ""
	check_file(src)
	dest = dest or paths.OUTPUT_PATH
	file_md5 = get_apk_md5(src)	
	
	#info_msg = "target apk file md5:%s" %file_md5
	#logger.info(info_msg)
	
	apk_decoded_file = "%s" %file_md5
	apk_decoded_path = os.path.join(dest, apk_decoded_file)
	
	if not flush and os.path.exists(apk_decoded_path):
		ret = apk_decoded_path
		info_msg = "load decoded files from '%s'" %apk_decoded_path
		logger.info(info_msg)	
		return ret
			
	try:
		apktool_postfix = ".bat" if IS_WIN else ""
		apktool_bin = os.path.join(conf.apktool_path,'apktool' + apktool_postfix)
		if not os.path.exists(apktool_bin):
			err_msg = "apktool file is not exists in path[%s]" %conf.apktool_path
			logger.error(err_msg)
			return ret	
		
		cmd = '%s d -s -f "%s" "%s"' %(apktool_bin, src, apk_decoded_path)
		
		info_msg = "decode apk file '%s'" %src
		logger.info(info_msg)	
		
		process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE, close_fds=False)
		if not async:
			process.wait()
			
		ret = apk_decoded_path
		
		time.sleep(1)
		info_msg = "unzip 'classes.dex' file to '%s'" %apk_decoded_path
		logger.info(info_msg)
		unzip(src, apk_decoded_path,dex=True)
		time.sleep(1)
		
		return ret
	except Exception,e:
		print e
	
	return ret		

def dex2jar(src, dest, flush=False, async=False):
	"""
	decode dex to jar
	"""
	ret = ""
	check_file(src)
	dest = dest or paths.OUTPUT_PATH
	if not flush and os.path.exists(dest):
		ret = dest
		info_msg = "load dex file from '%s'" %src
		logger.info(info_msg)	
		return ret	
	
	try:
		dex2jar_bin = os.path.join(conf.dex2jar_path,'d2j-dex2jar.sh')
		if not os.path.exists(dex2jar_bin):
			err_msg = "dex2jar file is not exists in path[%s]" %conf.dex2jar_path
			logger.error(err_msg)
			return ret	
		
		cmd = '%s %s -f -n -o "%s"' %(dex2jar_bin, src, dest)
		
		info_msg = "dump dex file [%s] to jar file" %src
		logger.info(info_msg)	
		
		process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE, close_fds=False)
		if not async:
			process.wait()
				
		ret = dest
		time.sleep(1)
		return ret
	except Exception,e:
		print e
	
	return ret

def jad(src, dest, flush=False, async=False):
	"""
	decode java
	"""
	ret = ""
	check_file(src)
	dest = dest or paths.OUTPUT_PATH
	
	class_output = os.path.join(dest,'class')
	src_output = os.path.join(dest,'src')	

	if not flush and not is_dir_empty(src_output):
		ret = dest
		info_msg = "load decoded java class files from '%s'" %class_output
		logger.info(info_msg)	
		return ret	
	
	try:
		jad_bin = os.path.join(conf.jad_path,'jad')
		if not os.path.exists(jad_bin):
			err_msg = "jad file is not exists in path[%s]" %conf.jad_path
			logger.error(err_msg)
			return ret
				
		unzip(src,class_output)		
		cmd = '%s -o -r -d "%s" -s java "%s/**/*.class"' %(jad_bin, src_output, class_output)
		info_msg = "decode class file to '%s'" %src_output
		logger.info(info_msg)
		
		process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE, close_fds=False)
		
		try:
			run_wait(process, timeout=conf.timeout)
		except ApkscanTimeoutException:
			warn_msg = "run jad decode process timeout[%ss],kill process pid[%s] and child processes" %(conf.timeout, process.pid)
			logger.warn(warn_msg)
						
			kill_child_processes(process.pid)
			
			process.kill()
			process.wait()

		if not async:
			process.wait()
		
		ret = src_output
		time.sleep(1)
		return ret
	
	except Exception,e:
		print e
	
	return ret

def get_package():
	return kb.apk.package['name']

def check_tag(xml_obj,tag_name):
	ret = False
	if xml_obj.getElementsByTagName(tag_name):
		ret = True
	return ret

def get_intent_filter_elements(xml_obj, tag_name, element="action", where=()):
	ret = []
	for item in xml_obj.getElementsByTagName(tag_name):
		if where:
			where_tag = where[0]
			where_value = where[1]
			value = item.getAttribute(where_tag)
			value = format_value(get_package(), value)
			if value != where_value:
				continue
			
		filters = item.getElementsByTagName('intent-filter')
		# [<DOM Element: intent-filter at 0x8e5df0c>]
		if filters:
			for node in filters:
				for value in node.getElementsByTagName(element):
					attr_value = get_unicode(value.getAttribute('android:name'))
					ret.append(attr_value)
								
		return ret
	
def get_element_value(xml_obj, tag_name, attribute,where=()):
	for item in xml_obj.getElementsByTagName(tag_name):
		if where:
			where_tag = where[0]
			where_value = where[1]
			value = item.getAttribute(where_tag)
			value = format_value(get_package(), value)
			if value != where_value:
				continue
		value = get_unicode(item.getAttribute(attribute))
		if len(value) > 0:
			return value
	return None
	
def get_element(xml_obj, tag_name, attribute):
	for item in xml_obj.getElementsByTagName(tag_name):
		value = get_unicode(item.getAttribute(attribute))
		if len(value) > 0:
			return value
	return None

def get_elements(xml_obj, tag_name, attribute):
	ret = []
	for item in xml_obj.getElementsByTagName(tag_name):
		value = item.getAttribute(attribute)
		value = format_value(get_package(), value)
		value = get_unicode(value)
		ret.append(value)
		
	return ret

def format_value(package, value):
	if len(value) > 0:
		if value[0] == ".":
			value = package + value
		else:
			v_dot = value.find(".")
			if v_dot == 0:
				value = package + "." + value
			elif v_dot == -1:
				value = package + "." + value
				
	return value	
	
def get_apk_providers(xml_obj):
	return get_elements(xml_obj, "provider", "android:name")

def get_apk_receivers(xml_obj):
	return get_elements(xml_obj, "receiver", "android:name")

def get_apk_services(xml_obj):
	return get_elements(xml_obj, "service", "android:name")

def get_apk_activities(xml_obj):
	return get_elements(xml_obj, "activity", "android:name")

def get_apk_actions(xml_obj):
	return get_elements(xml_obj, "action", "android:name")
	
def get_apk_permissions():
	return kb.apk['uses-permission']

def adb_install(src, async=False):
	"""
	adb install apk file
	"""
	pass

def adb_uninstall(apkfile, async=False):
	"""
	adb uninstall apk file
	"""
	pass

def adb_shell(cmd):
	"""
	adb shell
	"""
	pass

def run_avd(avd, async=False):
	"""
	run avd emulator
	"""
	pass

def sign_apk(apkfile, pem=None, pk=None, quiet=False, desc=None, async=False):
	"""
	sign apk file
	"""	
	pass

	