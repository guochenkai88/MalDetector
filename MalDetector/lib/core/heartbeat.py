#!/usr/bin/env python
#coding:utf-8
# Author:   hysia--<>
# Purpose:
# Created: 2012年12月31日

import time
import socket
from lib.core.datatype import AttribDict

class HeartBeat(AttribDict):
	"""
	发送心跳，和调度通讯
	"""
	#----------------------------------------------------------------------
	def __init__(self,connectStr):
		"""Constructor"""
		super(HeartBeat, self).__init__()
		self.START = "C77DA9EB-8E5A-4a8e-92A7-7C2CD2745E7A\n"
		self.HEARTBEAT = "47C1F778-D399-447b-B4A5-E1FAEF395F83\n"
		self.EXCEPTION = "B4BE4E85-C7C3-4f97-81E4-127E68EADDE2\n"
		self.COMPLETE = "2873E5E7-8721-4C47-BF3D-E467D67733C6\n"
		hostnamePort = connectStr.split(':')
		self.host = hostnamePort[0] if len(hostnamePort)==2 else None
		self.port = int(hostnamePort[1]) if len(hostnamePort)==2 else None
		self.sock = None
		self._connect()

	def _connect(self):
		""""""
		if self.host and self.port:
			try:
				self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.sock.connect((self.host, self.port))
				infoMsg = '[heartbeat] connected to server %s:%s.' %(self.host,self.port)
				print infoMsg
				return True
			except:
				self.sock = None
				errMsg = "[heartbeat] connect to server %s:%s failed" %(self.host,self.port)
				print errMsg
				return False


	def sendBeat(self,value):
		"""send socket"""
		if self.sock:
			try:
				if value:
					self.sock.sendall(value)
				return True
			except:
				errMsg = "[heartbeat] send heartbeat failed."
				print errMsg
				return False
		else:
			print "[heartbeat] connect error.check your socket connection "
			return False

	def close(self):
		"""close sock"""
		if self.sock:
			try:
				self.sock.close()
			except:
				self.sock = None


def testServer():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('localhost', 8629))
	sock.listen(5)
	while True:
		print "Waiting for connection..."
		connection,address = sock.accept()
		try:
			print "Waiting for data"
			buf = connection.recv(1024)
			print buf
			if buf == 'B4BE4E85-C7C3-4f97-81E4-127E68EADDE2\n':
				print "Quit msg."
				break
		except:
			continue

if __name__ == '__main__':
	testServer()
	#heartbeat = HeartBeat('127.0.0.1:8629')
	#heartbeat.sendBeat(heartbeat.HEARTBEAT)






