#!/usr/bin/env python
#coding:utf-8
# Author:  hysia --<zhouhaixiao@baidu.com>
# Purpose: 
# Created: 09/17/2013

class ApkscanBaseException(Exception):
    pass

class ApkscanCompressionException(ApkscanBaseException):
    pass

class ApkscanConnectionException(ApkscanBaseException):
    pass

class ApkscanDataException(ApkscanBaseException):
    pass

class ApkscanFilePathException(ApkscanBaseException):
    pass

class ApkscanGenericException(ApkscanBaseException):
    pass

class ApkscanMissingDependence(ApkscanBaseException):
    pass

class ApkscanMissingMandatoryOptionException(ApkscanBaseException):
    pass

class ApkscanMissingPrivileges(ApkscanBaseException):
    pass

class ApkscanNoneDataException(ApkscanBaseException):
    pass

class ApkscanNotVulnerableException(ApkscanBaseException):
    pass

class ApkscanSilentQuitException(ApkscanBaseException):
    pass

class ApkscanUserQuitException(ApkscanBaseException):
    pass

class ApkscanSyntaxException(ApkscanBaseException):
    pass

class ApkscanThreadException(ApkscanBaseException):
    pass

class ApkscanTimeoutException(ApkscanBaseException):
    pass

class ApkscanUndefinedMethod(ApkscanBaseException):
    pass

class ApkscanUnsupportedDBMSException(ApkscanBaseException):
    pass

class ApkscanUnsupportedFeatureException(ApkscanBaseException):
    pass

class ApkscanValueException(ApkscanBaseException):
    pass
