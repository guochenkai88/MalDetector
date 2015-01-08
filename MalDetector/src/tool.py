# -*- coding: UTF-8 -*-
import sys,string,os,shutil  
from permission_baseline import PERMISSION_LIST

def changeFileName(srcdir,prefix):
    '''
    change all the files' names under the given dictory
    '''
    try:  
        srcfiles = os.listdir(srcdir)  
        index = 1  
        for srcfile in srcfiles:  
            srcfile = srcfile.decode('gbk')
            print("source:" + srcfile.encode('gb2312'))  
            srcfilename = os.path.splitext(srcfile)[0][1:]  
            sufix = os.path.splitext(srcfile)[1]  
            #print(sufix)  
            destfile = srcdir + "\\" + prefix + "_%04d"%(index) + sufix  
            srcfile = srcdir + "\\" + srcfile  
            os.rename(srcfile,destfile)  
            index +=1  
            print("destination:" + destfile)  
    except:  
        print("please confirm your input!")  
    return 0
#----------------------------------------------------------------------
def  findPmsIndex(key_name):
    """
    permission_baseline is only saved as dict, sometime we need get the index of item according key name 
    """
    for item in range (0,len(PERMISSION_LIST)):
        if PERMISSION_LIST[item]['Key'].find(key_name)>=0 :
            return item
    
#p = changeFileName("D:\\app_malware\\samples","malware")
#print p

index = findPmsIndex("BLUETOOTH")
print index
    