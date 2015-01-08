#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

"""
convert functions
"""

import json
import pickle
import sys

from lib.core.settings import IS_WIN
from lib.core.settings import UNICODE_ENCODING

def base64decode(value):
	"""
	Decodes string value from Base64 to plain format

	>>> base64decode('Zm9vYmFy')
	'foobar'
	"""

	return value.decode("base64")

def base64encode(value):
	"""
	Encodes string value from plain to Base64 format

	>>> base64encode('foobar')
	'Zm9vYmFy'
	"""

	return value.encode("base64")[:-1].replace("\n", "")

def base64pickle(value):
	"""
	Serializes (with pickle) and encodes to Base64 format supplied (binary) value

	>>> base64pickle('foobar')
	'gAJVBmZvb2JhcnEALg=='
	"""

	ret = None
	try:
		ret = base64encode(pickle.dumps(value, pickle.HIGHEST_PROTOCOL))
	except:
		msg = "problem occurred while serializing "
		msg += "instance of a type '%s'" % type(value)
		print msg

		ret = base64encode(pickle.dumps(str(value), pickle.HIGHEST_PROTOCOL))
	return ret

def base64unpickle(value):
	"""
	Decodes value from Base64 to plain format and deserializes (with pickle) its content

	>>> base64unpickle('gAJVBmZvb2JhcnEALg==')
	'foobar'
	"""

	return pickle.loads(base64decode(value))

def hexdecode(value):
	"""
	Decodes string value from hex to plain format

	>>> hexdecode('666f6f626172')
	'foobar'
	"""

	value = value.lower()
	return (value[2:] if value.startswith("0x") else value).decode("hex")

def hexencode(value):
	"""
	Encodes string value from plain to hex format

	>>> hexencode('foobar')
	'666f6f626172'
	"""

	return utf8encode(value).encode("hex")

def unicodeencode(value, encoding=None):
	"""
	Returns 8-bit string representation of the supplied unicode value

	>>> unicodeencode(u'foobar')
	'foobar'
	"""

	ret = value
	if isinstance(value, unicode):
		try:
			ret = value.encode(encoding or UNICODE_ENCODING)
		except UnicodeEncodeError:
			ret = value.encode(UNICODE_ENCODING, "replace")
	return ret

def utf8encode(value):
	"""
	Returns 8-bit string representation of the supplied UTF-8 value

	>>> utf8encode(u'foobar')
	'foobar'
	"""

	return unicodeencode(value, "utf-8")

def utf8decode(value):
	"""
	Returns UTF-8 representation of the supplied 8-bit string representation

	>>> utf8decode('foobar')
	u'foobar'
	"""

	return value.decode("utf-8")

def htmlunescape(value):
	"""
	Returns (basic conversion) HTML unescaped value

	>>> htmlunescape('a&lt;b')
	'a<b'
	"""

	retVal = value
	if value and isinstance(value, basestring):
		codes = (('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ('&nbsp;', ' '), ('&amp;', '&'))
		retVal = reduce(lambda x, y: x.replace(y[0], y[1]), codes, retVal)
	return retVal

def stdoutencode(data):
	ret = None

	try:
		# Reference: http://bugs.python.org/issue1602
		if IS_WIN:
			output = data.encode("ascii", "replace")

			if output != data:
				msg = "cannot properly display Unicode characters "
				msg += "inside Windows OS command prompt "
				msg += "(http://bugs.python.org/issue1602). All "
				msg += "unhandled occurances will result in "
				msg += "replacement with '?' character. Please, find "
				msg += "proper character representation inside "
				msg += "corresponding output files. "
				print msg

			ret = output
		else:
			ret = data.encode(sys.stdout.encoding)
	except:
		ret = data.encode(UNICODE_ENCODING)

	return ret

def jsonize(data):
	"""
	Returns JSON serialized data

	>>> jsonize({'foo':'bar'})
	'{\\n    "foo": "bar"\\n}'
	"""

	return json.dumps(data, sort_keys=False, indent=4)

def dejsonize(data):
	"""
	Returns JSON deserialized data

	>>> dejsonize('{\\n    "foo": "bar"\\n}')
	{u'foo': u'bar'}
	"""

	return json.loads(data)