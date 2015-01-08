#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

import inspect
import logging
import os
import sys
import time
import traceback
import warnings

reload(sys)  
sys.setdefaultencoding('utf8')   

warnings.filterwarnings(action="ignore", message=".*was already imported", category=UserWarning)
warnings.filterwarnings(action="ignore", category=DeprecationWarning)

from lib.utils import envcheck  # this has to be the first non-standard import

from lib.controller.controller import start
from lib.core.common import banner
from lib.core.common import data_stdout
from lib.core.common import get_unicode
from lib.core.common import set_color
from lib.core.common import set_paths
from lib.core.common import we_are_frozen
from lib.core.data import cmd_options
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import result
from lib.core.data import logger
from lib.core.data import paths
from lib.core.common import unhandled_exception_message
from lib.core.common import send_heartbeat
from lib.core.exception import ApkscanBaseException
from lib.core.exception import ApkscanSilentQuitException
from lib.core.exception import ApkscanUserQuitException
from lib.core.option import init_options
from lib.core.option import init
from lib.parse.cmdline import cmd_parser

def module_path():
	"""
	This will get us the program's directory, even if we are frozen
	using py2exe
	"""

	try:
		_ = sys.executable if we_are_frozen() else __file__
	except NameError:
		_ = inspect.getsourcefile(module_path)

	return os.path.dirname(os.path.realpath(get_unicode(_, sys.getfilesystemencoding())))

def main():
	"""
	Main function of apkscan when running from command line.
	"""
	try:
		paths.ROOT_PATH = module_path()
		set_paths()
		
		# Store original command line options for possible later restoration
		cmd_options.update(cmd_parser().__dict__)
		init_options(cmd_options)
		
		banner()
		
		data_stdout("[*] starting at %s\n\n" % time.strftime("%X"), forceOutput=True)
		
		init()
		start()
		
	except ApkscanUserQuitException:
		err_msg = "user quit"
		logger.error(err_msg)
		
	except ApkscanBaseException, ex:
		err_msg = get_unicode(ex.message)
		logger.critical(err_msg)
		sys.exit(1)
		
	except KeyboardInterrupt:
		print
		err_msg = "user aborted"
		logger.error(err_msg)
		
	except EOFError:
		print
		err_msg = "exit"
		logger.error(err_msg)
		
	except SystemExit:
		pass
	
	except:
		print
		err_msg = unhandled_exception_message()
		logger.critical(err_msg)
		data_stdout(set_color(traceback.format_exc()))
		
	finally:
		data_stdout("\n[*] shutting down at %s\n\n" % time.strftime("%X"), forceOutput=True)
		send_heartbeat(close=True)
		if kb.storage:
			kb.storage.quit()
		
if __name__=='__main__':
	main()