#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

import codecs
import os
import re
import sys
import time
import logging
import zipfile
import signal
import urlparse
import urllib
import urllib2
import json
from hashlib import md5
from xml.dom import minidom

#import psutil

from lib.core.data import paths
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import result
from lib.core.data import logger
from lib.core.convert import stdoutencode
from lib.core.exception import ApkscanFilePathException
from lib.core.exception import ApkscanValueException
from lib.core.exception import ApkscanTimeoutException
from lib.core.log import LOGGER_HANDLER
from lib.core.permissions import PERMISSION_LIST
from lib.core.settings import NULL
from lib.core.settings import UNICODE_ENCODING
from lib.core.settings import INVALID_UNICODE_CHAR_FORMAT
from lib.core.settings import VERSION_STRING
from lib.core.settings import DESCRIPTION
from lib.core.settings import PLATFORM
from lib.core.settings import PYVERSION

from thirdparty.termcolor.termcolor import colored

def extract_regex_result(regex, content, flags=0):
	"""
	Returns 'result' group value from a possible match with regex on a given
	content

	>>> extractRegexResult(r'a(?P<result>[^g]+)g', 'abcdefg')
	'bcdef'
	"""

	ret = None

	if regex and content and "?P<result>" in regex:
		match = re.search(regex, content, flags)

		if match:
			ret = match.group("result")

	return ret

def is_list_like(value):
	"""
	Returns True if the given value is a list-like instance

	>>> is_list_like([1, 2, 3])
	True
	>>> is_list_like(u'2')
	False
	"""

	return isinstance(value, (list, tuple, set))

def get_unicode(value, encoding=None, system=False, none_to_null=False):
	"""
	Return the unicode representation of the supplied value:

	>>> get_unicode(u'test')
	u'test'
	>>> get_unicode('test')
	u'test'
	>>> get_unicode(1)
	u'1'
	"""

	if none_to_null and value is None:
		return NULL

	if is_list_like(value):
		value = list(get_unicode(_, encoding, system, none_to_null) for _ in value)
		return value

	if not system:
		if isinstance(value, unicode):
			return value
		elif isinstance(value, basestring):
			while True:
				try:
					return unicode(value, encoding or UNICODE_ENCODING)
				except UnicodeDecodeError, ex:
					value = value[:ex.start] + "".join(INVALID_UNICODE_CHAR_FORMAT % ord(_) for _ in value[ex.start:ex.end]) + value[ex.end:]
		else:
			return unicode(value)  # encoding ignored for non-basestring instances
	else:
		try:
			return get_unicode(value, sys.getfilesystemencoding() or sys.stdin.encoding)
		except:
			return get_unicode(value, UNICODE_ENCODING)

def set_color(message, bold=False):
	ret = message
	level = extract_regex_result(r"\[(?P<result>[A-Z ]+)\]", message)

	if message and getattr(LOGGER_HANDLER, "is_tty", False):  # colorizing handler
		if bold:
			ret = colored(message, color=None, on_color=None, attrs=("bold",))
		elif level:
			level = getattr(logging, level, None) if isinstance(level, basestring) else level
			_ = LOGGER_HANDLER.level_map.get(level)
			if _:
				background, foreground, bold = _
				ret = colored(message, color=foreground, on_color="on_%s" % background if background else None, attrs=("bold",) if bold else None)
	return ret	

def data_stdout(data, forceOutput=False, bold=False):
	"""
	Writes text to the stdout (console) stream
	"""
	message = data
	if isinstance(data, unicode):
		message = stdoutencode(data)
	else:
		message = data

	sys.stdout.write(set_color(message, bold))

	try:
		sys.stdout.flush()
	except IOError:
		pass

def unhandled_exception_message():
	"""
	Returns detailed message about occurred unhandled exception
	"""
	msg = "unhandled exception in %s \n" % VERSION_STRING
	msg += "Python version: %s\n" % PYVERSION
	msg += "Operating system: %s\n" % PLATFORM
	msg += "Command line: %s\n" % " ".join(sys.argv)
	
	return msg

def we_are_frozen():
	"""
	Returns whether we are frozen via py2exe.
	This will affect how we find out where we are located.
	Reference: http://www.py2exe.org/index.cgi/WhereAmI
	"""

	return hasattr(sys, "frozen")

def banner():
	
	_ = """\n    %s - %s\n\n""" % (VERSION_STRING, DESCRIPTION)
	data_stdout(_, forceOutput=True)
	
def set_paths():
	"""
	Sets absolute paths for project directories and files
	"""
	paths.OUTPUT_PATH = os.path.join(paths.ROOT_PATH, "output")	
	paths.PLUGINS_PATH = os.path.join(paths.ROOT_PATH, "plugins")
	paths.RULES_PATH = os.path.join(paths.ROOT_PATH, "rules")
	paths.THIRD_PARTY = os.path.join(paths.ROOT_PATH, "thirdparty")
	#files
	paths.CONFIG_FILE = os.path.join(paths.ROOT_PATH, "default.config.yaml")
	
def check_file(filename):
	"""
	@param filename: filename to check if it exists.
	@type filename: C{str}
	"""

	if not os.path.exists(filename):
		raise IOError, "unable to read file '%s'" % filename
	
def get_file_items(filename, comment_prefix='#'):
	ret = []

	check_file(filename)
	ifile = open(filename, 'r')

	for line in ifile.readlines():
		if comment_prefix:
			if line.find(comment_prefix) != -1:
				line = line[:line.find(comment_prefix)]
		line = line.strip()
		#if line:
		ret.append(line)

	return ret

def get_file_content(filename, mode='r'):
	"""
	Returns file content of a given filename
	"""
	ret = None
	try:
		fp = codecs.open(filename, mode, UNICODE_ENCODING, "replace")
		ret = fp.read()
	except IOError:
		err_msg = "there has been a file opening error for filename '%s'. " % filename
		err_msg += "Please check %s permissions on a file " % ("write" if \
				                                              mode and ('w' in mode or 'a' in mode or '+' in mode) else "read")
		err_msg += "and that it's not locked by another process."
		raise ApkscanFilePathException, err_msg
	return ret	

def md5_sum(file_path):
	"""
	md5 sum
	"""
	check_file(file_path)
	statinfo = os.stat(file_path)
	if int(statinfo.st_size)/(1024*1024) >= 1000 :
		return md5_sum_bigfile(file_path)
	
	m = md5()
	f = open(file_path, 'rb')
	m.update(f.read())
	f.close()
	return m.hexdigest()

def md5_sum_bigfile(file_path):
	m = md5()
	f = open(file_path, 'rb')
	buffer = 8192
	while True:
		data = f.read(buffer)
		if not data:
			break
		m.update(data)
	f.close()
	
	return m.hexdigest()

def get_apk_md5(file_path):
	"""
	get apk file md5
	"""
	ret = None
	
	if kb.apk.md5 is None:
		kb.apk.md5 = md5_sum(file_path)
		ret = md5_sum(file_path)
	else:
		ret = kb.apk.md5
		
	return ret

def get_apk_size(file_path):
	
	ret = None
	check_file(file_path)
	
	if kb.apk.file_size is None:
		size = os.path.getsize(file_path)
		kb.apk.file_size = '%.1fKB' % (size/1024)
	else:
		ret = kb.apk.file_size
	
	return ret

def parse_apk_info(data):
	"""
	parse aapt output to kb.apk
	"""
	if not data:
		warn_msg = 'aapt output without data'
		logger.warn(warn_msg)
		return
	
	try:
		lines = data.split('\n')
		for line in lines:
			line = line.strip()
			if not line:
				continue
			
			elems = line.split(':')
			if len(elems) != 2:
				debug_msg = "value '%s' is not correct format, pass." %line
				logger.debug(debug_msg)
				continue
			
			key = elems[0].strip()
			value = elems[1].strip()
			value = value.strip("'") if " " not in value else value
			value = get_unicode(value)
			if '=' not in value:						
				if key not in kb.apk:				
					kb.apk[key] = value
				else:
					org_value = kb.apk[key]
					if isinstance(org_value,list):
						if isinstance(value,list):
							kb.apk[key].extend(value)
						else:
							kb.apk[key].append(value)
					else:
						kb.apk[key] = []
						kb.apk[key].append(org_value)
						if isinstance(value,list):
							kb.apk[key].extend(value)
						else:
							kb.apk[key].append(value)
			else:
				items = value.split(' ')
				for item in items:
					item = item.strip()
					if not item:
						continue
					attrs = item.split('=')
					if len(attrs) == 2:
						attr = attrs[0]
						attr_value = attrs[1].strip("'")
						
						if key not in kb.apk:
							kb.apk[key] = {}
							kb.apk[key][attr] = attr_value
						else:
							kb.apk[key][attr] = attr_value
		
		if isinstance(kb.apk['uses-permission'],basestring):
			kb.apk['uses-permission'] = [kb.apk['uses-permission']]
		kb.apk['uses-permission'].sort()
		kb.apk.display_perm = [i for i in PERMISSION_LIST if i['Key'] in kb.apk['uses-permission'] ]
		kb.apk.sdkVersion = None if 'sdkVersion' not in kb.apk else kb.apk.sdkVersion
		kb.apk.targetsdkVersion = None	if 'targetsdkVersion' not in kb.apk else kb.apk.targetsdkVersion
		
	except Exception,e:
		print e
				
def init_apk_info(data):
	"""
	init kb.apk data
	"""
	parse_apk_info(data)
	#get_apk_md5(conf.apk)
	get_apk_size(conf.apk)
	
	
def show_perm_info(perm):
	"""
	show PERMISSION
	"""
	ret = {}
	if not perm:
		return ret
	
	for p in PERMISSION_LIST:
		if perm == p['Key']:
			ret = p
			break
		
	return ret

def show_risk_info(level):
	
	if int(level) == 0:
		ret = u'安全'
	elif int(level) == 1:
		ret = u'低危'
	elif int(level) == 2:
		ret = u'中危'	
	elif int(level) == 3:
		ret = u'高危'
	else:
		ret = u'未知'
		
	return ret

def zipdir(src, dest):
	ret = False
	if src and dest and os.path.exists(src):		  
		f = zipfile.ZipFile(dest,'w')
		
		for root, dirs, files in os.walk(src):
			for fi in files:
				abs_path = os.path.join(os.path.join(root, fi))
				rel_path = os.path.relpath(abs_path, os.path.dirname(src))
				f.write(abs_path, rel_path, zipfile.ZIP_STORED)

		f.close()
		ret = True
	else:
		err_msg = "zip dir '%s' failed" %src
		logger.error(err_msg)
	return ret
	
def unzip(src, dest, dex=False):
	"""
	unzip a zipped file
	"""
	if zipfile.is_zipfile(src):
		if dex:
			f = zipfile.ZipFile(src)
			if "classes.dex" in f.namelist():
				f.extract('classes.dex',dest)
			else:
				err_msg = "'classes.dex' not in target zip file:%s" %src
				raise ApkscanValueException, err_msg			
			return 
		else:	
			f = zipfile.ZipFile(src)
			f.extractall(dest) 
			f.close()
	else:
		err_msg = "target file '%s' is not a zip file" %src
		raise ApkscanValueException, err_msg		
	
def is_dir_empty(dir_path):
	if os.path.exists(dir_path):
		for root,dirs,files in os.walk(dir_path):
			if dirs == [] and files ==[]:
				return True
	else:
		err_msg = "file path:'%s' is not exists" %dir_path
		raise ApkscanFilePathException, err_msg
	
def run_wait(process, timeout, _sleep_time=.1):
	for _ in xrange(int(timeout * 1. / _sleep_time + .5)):
		time.sleep(_sleep_time)  # NOTE: assume it doesn't wake up earlier
		if process.poll() is not None:
			return process.wait()
	raise ApkscanTimeoutException  # NOTE: timeout precision is not very good

def kill_child_processes(parent_pid, sig=signal.SIGTERM):
	try:
		p = psutil.Process(parent_pid)
	except psutil.error.NoSuchProcess:
		return
	child_pid = p.get_children(recursive=True)
	for pid in child_pid:
		os.kill(pid.pid, sig)
		
def save_result(file_path=None):
	"""
	write result
	"""	
	if not conf.result_path:
		filename = "%s_%s.txt" %(kb.apk.package['name'], kb.apk.package['versionName'])
		filename = filename.decode('utf8')
		conf.result_path = os.path.join(file_path, filename) if file_path else os.path.join(paths.OUTPUT_PATH, filename)
		conf.result_path = conf.result_path.encode('utf8') \
		    if isinstance(conf.result_path, unicode) else conf.result_path
		
	with open(conf.result_path,'w') as f:		
		line ="apk name: %s" %kb.apk.application['label']
		line +="\napk version: %s" %kb.apk.package['versionName']
		line +="\napk md5 signature: %s"  %kb.apk.md5
		line +="\nrisks:"
		f.write('%s\n' %line.encode('utf8'))		
		for i in result.plugins:
			risk = show_risk_info(i['risk'])
			f.write('%s  [%s]\n' %(i['name'].encode('utf8'), risk.encode('utf8')))
			if 'data' in i:
				for data in i['data']:
					f.write('    * %s\n' %(data.encode('utf8')))
	
	conf.result_path = "" #modified by guo: clear result path for next apk.
	
def save_pms_as_arff(file_path=None, target_path=None):
	"""
	write result
	"""	
	if not conf.pms_result_path:
		#filename = "permission.arff" 
		filename = "discussions_permission.txt" 
		filename = filename.decode('utf8')
		conf.pms_result_path = os.path.join(file_path, filename) if file_path else os.path.join(paths.OUTPUT_PATH, filename)
		conf.pms_result_path = conf.pms_result_path.encode('utf8') \
		    if isinstance(conf.pms_result_path, unicode) else conf.pms_result_path
	#if not os.path.isfile(conf.pms_result_path):
		#with open(conf.pms_result_path,'w+') as f:
			#f.write('@relation permissions\n')
			#for i in PERMISSION_LIST:
				#f.write('@attribute '+ i['Key'] +' {1,0}\n')
			#f.write('@data\n')	
	
	with open(conf.pms_result_path,'a+') as f:
		#line = kb.apk.application['label']
		line = kb.apk.package['name']
		#line = target_path
		f.write(str(line) + '\n')
		for i in PERMISSION_LIST:
			if i in kb.apk.display_perm:		
				f.write('1 ')
			else: f.write('0 ')						
		f.write('\n')
		
		
		
		
			
def get_xml_obj(decoded_files):
	
	ret = None
	xmlfile = os.path.join(decoded_files,'AndroidManifest.xml')
	check_file(xmlfile)
	
	content = get_cached_file_content(xmlfile)	
	try:
		ret = minidom.parseString(content)
				
	except:
		warn_msg = "parse xml file error: %s" %xmlfile
		logger.warn(warn_msg)
		
	return ret

def get_cached_file_content(filename):
	ret = None
	if filename in kb.cache.files:
		ret = kb.cache.files[filename]
	else:
		ret = get_file_content(filename)
		kb.cache.files[filename] = ret
		
	return ret

def send_heartbeat(start=False, close=False):
	"""
	send heartbeart to monitor server
	"""
	if 'heartbeat' in kb and kb.heartbeat:
		if start:
			kb.heartbeat.sendBeat(kb.heartbeat.START)
			return
		if close:
			kb.heartbeat.sendBeat(kb.heartbeat.COMPLETE)
			time.sleep(1)
			kb.heartbeat.close()			
			return
		else:
			kb.heartbeat.sendBeat(kb.heartbeat.HEARTBEAT)
							
def upload_result(api_url, tid, module, obj={}):
	"""
	api upload
	"""
	ret = False
	MODULES = ['static_scan','dynamic_scan']
	
	if api_url and tid and module:
		if module.lower() not in MODULES:
			errMsg = "api save param 'module' should be in %s" %MODULES
			print errMsg
			return retVal
		
		path = '/mapi/v2/tasks/%s/set_result/%s' %(tid, module)
		url = urlparse.urljoin(api_url, path)
		data = json.dumps(obj,ensure_ascii=False)
		data = data.encode('utf8')
		postdata = {'result':data}
		postdata = urllib.urlencode(postdata)
		
		req = urllib2.Request(url, postdata)
		for i in range(3):
			try:
				response = urllib2.urlopen(req)
				jdata = json.load(response)
			except:
				jdata = None
	
			if jdata:
				if jdata['status'] == 'ok':
					ret = True
					break
				else:
					errMsg = "api save result failed. msg:%s" %jdata.get('msg')
					logger.error(errMsg)
					time.sleep(1)
			else:
				errMsg = "get api server http response error"
				errMsg += " request try again."
				logger.error(errMsg)
				time.sleep(1)		
	else:
		errMsg = "api save need params (api_url, tid, module)"
		print errMsg
		
	return ret

def get_smali_file(name):
	"""
	com.baidu.browser.framework.BdBrowserActivity -> smali/com/baidu/browser/framework/BdBrowserActivity.smali
	"""
	if not name or '.' not in name:
		return None
	
	short_path = name.replace('.','/')
	full_path = 'smali/%s.smali' %short_path
	
	return full_path