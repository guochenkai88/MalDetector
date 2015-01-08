#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose:
# Created: 2012年12月31日

import codecs
from thirdparty import yaml
from lib.core.common import check_file
from lib.core.data import conf
from lib.core.data import logger
from lib.core.data import paths
from lib.core.exception import ApkscanMissingMandatoryOptionException
from lib.core.settings import UNICODE_ENCODING

config = None

config_dict = {
    "base":{
        "debug":"boolean",
        "verbose":"integer",
        "tid":"string",
        "threads":"integer",
        "monitor":"string",
        "mode":"string",
    },
    "target":{
        "apk":"string",
        "apk_path":"string",
        "config_file":"string",
    },
    "process":{
        "timeout":"integer",
        "result_path":"string",
        "pms_result_path":"string",
        "nfs_path":"string",
        "dex2jar":"boolean",
        "jad":"boolean",
        "apktool_path":"string",
        "dex2jar_path":"string",
        "jad_path":"string",
        "android_sdk_path":"string",

    },
    "plugins":{
    },
    "log":{
        "level":"string",
        "formatter":"string",
        "handlers":"string",
        "log_file":"string",
        "log_file_max_bytes":"integer",
        "log_file_backup_count":"integer",
        "sys_log_address":"tuple",
    },
    "storage":{
        "path":"string",
        "ftp_host":"string",
        "ftp_port":"integer",
        "ftp_user":"string",
        "ftp_passwd":"string",
        "api_url":"string",
    },

}

def yaml2object(filename):
	"""
	parse yaml file to python object
	>>> yaml2object(config.yaml)
	'{logger:{file:'xxx.log',level:'3',verbose:Fasle}}'
	"""
	try:
		fp = codecs.open(filename, "rb", UNICODE_ENCODING)
		yaml_object = yaml.load(fp)
		fp.close()
	except Exception,e:
		yaml_object = None
		err_msg = "incorrect format of yaml file:%s" %filename
		logger.error(err_msg)

	return yaml_object

def config_file_parser(config_file, override_options=False):
	"""
	Parse configuration file and save settings into the configuration
	advanced dictionary.
	"""
	global config

	debug_msg = "parsing configuration file: %s" %config_file
	logger.debug(debug_msg)

	check_file(config_file) #check if it exists

	config = yaml2object(config_file) #parse yaml file to python object

	if not 'target' in config:
		err_msg = "missing a mandatory section 'Target' in the configuration file"
		raise ApkscanMissingMandatoryOptionException, err_msg

	condition1 = config_file != paths.CONFIG_FILE \
	    and config.has_key('target') \
	    and config['target'].has_key('apk') \
	    and config['target'].get('apk',None) is None
	condition2 = config_file != paths.CONFIG_FILE \
	    and config.has_key('target') \
	    and config['target'].has_key('apk_path') \
	    and config['target'].get('apk_path',None) is None
	
	condition = condition1 and condition2
	
	if condition:
		err_msg = "missing a mandatory option in the configuration file "
		err_msg += "target apk file is required."
		raise ApkscanMissingMandatoryOptionException, err_msg

	for section, configData in config_dict.items():
		for option , datatype in configData.items():
			if config.has_key(section):
				if config[section].has_key(option):
					value = config[section][option]
					if value or override_options:
						conf[option] = value
			else:
				if override_options:
					debug_msg = "missing option '%s' (section " % option
					debug_msg += "'%s') into the configuration file, " % section
					debug_msg += "ignoring. Skipping to next."
					logger.debug(debug_msg)