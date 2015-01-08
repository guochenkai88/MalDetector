#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

import os
import sys

from optparse import OptionError
from optparse import OptionGroup
from optparse import OptionParser

from lib.core.common import get_unicode
from lib.core.data import logger
from lib.core.settings import IS_WIN
from lib.core.settings import VERSION_STRING

def cmd_parser():
	"""
	This function parses the command line parameters and arguments
	"""
	_ = os.path.normpath(sys.argv[0])
	
	usage = "%s%s [options]" % ("python " if not IS_WIN else "", \
	                            "\"%s\"" % _ if " " in _ else _)

	parser = OptionParser(usage=usage)

	try:
		parser.add_option("-v", dest="verbose", type="int", help="Verbosity level: 0-6 (default 1)")
		# Basic options
		basic = OptionGroup(parser, "Basic", "Basic options")
		basic.add_option("--tid", dest="tid", type="int",help="Task id")
		basic.add_option("--monitor", dest="monitor", help="Monitor server, eg: 127.0.0.1:11230")

		# Target options
		target = OptionGroup(parser, "Target", "At least one of these "
		                     "options has to be provided to set the target(s)")

		target.add_option("-a", "--apk", dest="apk", help="Target apk file")
		target.add_option("-p", "--apkpath", dest="apk_path", help="Target apks path")
		target.add_option("-c", "--config", dest="config_file", help="Load options from a configuration YAML file")

		# Process options
		process = OptionGroup(parser, "Process", "These options can be used "
		                      "to specify how to process target apk")

		process.add_option("--timeout", dest="timeout", type="int",
		                   help="Seconds to wait before timeout to process target "
		                   "(default 60)")
		process.add_option("--result", dest="result_path", help="Results file storage")
		process.add_option("--nfs", dest="nfs_path", help="NFS file storage")
		process.add_option("--dex2jar", dest="dex2jar", action="store_true",
				                                help="dump dex file to jar")		
		process.add_option("--jad", dest="jad", action="store_true",
				                                        help="decode jar file to java source file")	
		
		# Plugin options
		plugins = OptionGroup(parser, "Plugins", "These "
		                      "options can be used to load plugins for check")

		plugins.add_option("--plugins", dest="plugins",
		                   help="load plugin list,available plugins: A,B,C")

		# Optimization options
		optimization = OptionGroup(parser, "Optimization", "These "
		                           "options can be used to optimize the "
		                           "performance of scanner")

		optimization.add_option("--threads", dest="threads", type="int",
		                        help="Max number of threads (default 1)")
		
		optimization.add_option("--disable-coloring", dest="disable_coloring", action="store_true",
				                        help="Disable console output coloring")		

		parser.add_option_group(basic)
		parser.add_option_group(target)
		parser.add_option_group(process)
		parser.add_option_group(plugins)
		parser.add_option_group(optimization)

		args = []

		for arg in sys.argv:
			args.append(get_unicode(arg, system=True))

		(args, _) = parser.parse_args(args)

		if not any((args.apk, args.apk_path, args.config_file)):
			err_msg = "missing a mandatory option (-a, -p, -c), use -h for help"
			parser.error(err_msg)

		return args

	except (OptionError, TypeError), e:
		parser.error(e)

	except SystemExit:
		# Protection against Windows dummy double clicking
		if IS_WIN:
			print "\nPress Enter to continue...",
			raw_input()
		raise

	debug_msg = "parsing command line"
	logger.debug(debug_msg)


