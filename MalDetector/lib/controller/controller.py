#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

import os
import sys
import time
import traceback

from lib.core.android import aapt
from lib.core.android import apktool
from lib.core.android import AndroidVersionMap
from lib.core.android import dex2jar
from lib.core.android import jad
from lib.core.android import get_apk_providers
from lib.core.android import get_apk_receivers
from lib.core.android import get_apk_services
from lib.core.android import get_apk_activities
from lib.core.android import get_apk_actions
from lib.core.common import check_file
from lib.core.common import init_apk_info
from lib.core.common import show_perm_info
from lib.core.common import save_result
from lib.core.common import upload_result
from lib.core.common import get_xml_obj
from lib.core.common import send_heartbeat
from lib.core.common import zipdir
from lib.core.convert import utf8encode
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import result
from lib.core.data import logger
from lib.core.data import paths
from lib.core.option import flush_env
from lib.controller.plugin import start_plugin

def start():
	"""
	controller start
	"""
	info_msg = "apkscan got a total of %s target apk file(s)" %len(kb.targets)
	logger.info(info_msg)
	
	for target in kb.targets:
		
		try:
			check_file(target)
			conf.apk = target
		except: 
			info_msg = "apk file has some problems!"
			logger.info ( info_msg )
			conf.apk = None
		#except:
			#info_msg = "fetch target apkfile from FTP server [%s]" %conf.ftp_host
			#logger.info(info_msg)
			
			#try:
				#target_file = kb.storage.get(target)
				#if target_file is not None and os.path.exists(target_file):
					#conf.apk = target_file
			#except:
				#conf.apk = None
				
		if not conf.apk:
			warn_msg = "target apk file is not exists,pass"
			logger.warn(warn_msg)
			continue
		
		flush_env()
		send_heartbeat()
		try:
			for i in range(3):
				data = aapt(conf.apk,async=False)
				if data:
					break
			
			if not data:
				error_msg = "parse apk failed. maybe is not a apkfile or aapt run error. check system env!"
				logger.error(error_msg)
				continue
				
			init_apk_info(data)
			avm = AndroidVersionMap()
			apk_sdk_version = avm.get_version(kb.apk.sdkVersion) if kb.apk.sdkVersion else ''
		
			info_msg ="apk name: %s" %kb.apk.application['label']
			info_msg +="\napk version: %s" %kb.apk.package['versionName']
			info_msg +="\napk package: %s" %kb.apk.package['name']
			info_msg +="\napk icon: %s" %kb.apk.application['icon']
			info_msg +="\napk size: %s" %kb.apk.file_size
			info_msg +="\napk min-sdk-version: %s (%s)" %(kb.apk.sdkVersion, apk_sdk_version)
			info_msg +="\napk md5 signature: %s"  %kb.apk.md5
			print utf8encode(info_msg)
			#print kb.apk['uses-permission'],len(kb.apk['uses-permission'])
			print "apk permissions:"
			for perm in kb.apk.display_perm:
				print '[+]', perm['Title']
				
			send_heartbeat()
			
			decoded_files = apktool(conf.apk, conf.nfs_path, async=False)
			
			xml_obj = get_xml_obj(decoded_files)
			kb.apk.manifest = xml_obj
			kb.apk.providers = get_apk_providers(xml_obj)
			kb.apk.receivers = get_apk_receivers(xml_obj)
			kb.apk.services = get_apk_services(xml_obj)
			kb.apk.activities = get_apk_activities(xml_obj)
			kb.apk.actions = get_apk_actions(xml_obj)
			
			print "APK Content Providers:"
			for i in kb.apk.providers:
				print '[+]', i
	
			print "APK Broadcast Receivers:"
			for i in kb.apk.receivers:
				print '[+]', i			
	
			print "APK Services:"
			for i in kb.apk.services:
				print '[+]', i	
				
			print "APK Activities:"
			for i in kb.apk.activities:
				print '[+]', i					
				
			if conf.dex2jar:
				send_heartbeat()
				
				info_msg = "start dex2jar decode process"
				logger.info(info_msg)
				
				dex_file = os.path.join(decoded_files,'classes.dex')
				jar_output_file = os.path.join(decoded_files,'classes_dex2jar.jar')
				jar_file = dex2jar(dex_file, jar_output_file, flush=False, async=False)
				kb.apk.jar_file = jar_file if jar_file else None
				kb.apk.dex_file = dex_file if dex_file else None
				
				info_msg = "dex2jar decode process complete"
				logger.info(info_msg)
				
			if conf.jad:
				send_heartbeat()
				
				info_msg = "start jad decode process"
				logger.info(info_msg)
				
				class_output = os.path.join(decoded_files,'class')
				src_output = os.path.join(decoded_files,'src')
				for floder in [class_output, src_output]:
					if not os.path.exists(floder):
						os.makedirs(floder)
					
				jad(jar_file, decoded_files, flush=False, async=False)
				
				info_msg = "jad decode process complete"
				logger.info(info_msg)
					
			info_msg = "start run plugins check"
			logger.info(info_msg)
			
			send_heartbeat()
			
			start_plugin(decoded_files,conf.apk)
			
			info_msg = "plugins check complete"
			logger.info(info_msg)
			
			send_heartbeat()
			
			info_msg = "saving result"
			logger.info(info_msg)
			
			save_result(decoded_files)
			
			if conf.api_url and conf.tid:
				info_msg = "store files to server [%s]" %conf.ftp_host
				logger.info(info_msg)
				try:
					icon_file_ext = kb.apk.application['icon'][-4:]
					icon_file = os.path.join(decoded_files,kb.apk.application['icon'])
					icon = 'apkicon/%s%s' %(kb.apk.md5,icon_file_ext)
					kb.storage.put(icon_file, icon)
					zip_file = os.path.join(paths.OUTPUT_PATH, '%s.zip' %kb.apk.md5)
					zipdir(decoded_files, zip_file)
					kb.storage.put(zip_file, '%s.zip' %kb.apk.md5)
					info_msg = "put zip file '%s' to storage successful" %zip_file
					logger.info(info_msg)
				except Exception,e:
					icon = None
					err_msg = "put zip file '%s' to storage failed" %zip_file
					logger.error(err_msg)
			
			if conf.api_url and conf.tid:
				info_msg = "upload result to API server [%s]" %conf.api_url
				logger.info(info_msg)
				
				post_obj = {}
				post_obj['task_id'] = conf.tid
				post_obj['result_content'] = []
				data = {}
				data['app_name'] = kb.apk.application['label']
				data['app_version'] = kb.apk.package['versionName']
				data['package_name'] = kb.apk.package['name']
				data['app_icon'] = icon or kb.apk.application['icon']
				data['app_risk'] = 1
				data['app_md5'] = kb.apk.md5
				data['file_size'] = kb.apk.file_size
				data['min_sdk_version'] = kb.apk.sdkVersion
				data['target_sdk_version'] = kb.apk.targetsdkVersion
				data['app_permissions'] = kb.apk['uses-permission']
				data['app_content_providers'] = kb.apk.providers
				data['app_broadcast_receivers'] = kb.apk.receivers
				data['app_services'] = kb.apk.services
				data['app_activities'] = kb.apk.activities
				data['app_vulns'] = result.plugins
				data['vul_count'] = len(result.plugins)
				post_obj['result_content'].append(data)
				
				_ = upload_result(conf.api_url, conf.tid, 'static_scan' ,post_obj)
				info_msg = "upload result [%s] successful" %kb.apk.md5 if _ else "upload result [%s] failed" %kb.apk.md5
				logger.info(info_msg)
		except:
			warn_msg = "parse apk file '%s' failed\n" %target
			warn_msg += traceback.format_exc()
			logger.warn(warn_msg)
			
	info_msg = "done"
	logger.info(info_msg)
	
	
	