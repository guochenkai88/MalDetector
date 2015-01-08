#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

import os
import sys
import time
import ftplib
import logging
import zipfile
import signal
from hashlib import md5

from lib.core.data import paths
from lib.core.data import conf
from lib.core.data import logger

class Storage(object):
	""""""

	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		self.connected = False
		self.handle = None
		self.host = conf.ftp_host
		self.port = conf.ftp_port if conf.ftp_port else 21
		self.user = conf.ftp_user
		self.passwd = conf.ftp_passwd
		
		if not self.connected:
			try:
				self._connect()
				self.connected = True
			except Exception,e:
				err_msg = "Storage connect failed! rasie:'%s'" %e
				logger.error(err_msg) 
				
	def _connect(self):
		ftp = ftplib.FTP()
		ftp.connect(self.host, self.port, timeout=10)
		ftp.login(self.user, self.passwd)
		#ftp.set_pasv(True)
		self.handle = ftp
		
	def list_file(self):
		ret = []
		if self.handle:			 
			ret = self.handle.nlst()
		else:
			self._connect()
			ret = self.handle.nlst()
		return ret
	
	def has_file(self, filename):
		if self.handle:
			file_list = self.handle.nlst()
			return filename in file_list
		else:
			self._connect()
			file_list = self.handle.nlst()
			return filename in file_list
				
	def get(self, dest):
		ret = None
		bufsize = 1024
		file_save = os.path.join(paths.OUTPUT_PATH, dest)
		try:
			f = open(file_save,'wb').write
			self.handle.retrbinary('RETR %s' % os.path.basename(dest),f,bufsize)
			ret = file_save
		except:
			err_msg = "ftp download file '%s' failed! " %dest
			logger.error(err_msg)
			
		return ret
	
	def put(self, src, dest):
		try:
			f = open(src, 'rb')
			self.handle.storbinary('STOR %s' %dest, f)
		except:
			err_msg = "ftp upload file '%s' failed! " %src
			logger.error(err_msg)			
		finally:
			f.close()
				
	def quit(self):
		if self.handle:
			self.handle.quit()
			self.connected = False
			self.handle = None
	