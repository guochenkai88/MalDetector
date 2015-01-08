# computing single score using linear model


import os
#import signal
import time
from subprocess import PIPE
from lib.core.subprocessng import Popen
from apriori_mod import get_diff_pms
from lib.core.data import conf
from lib.core.data import paths
"""
Purpose: score for a single app or a path of apps' set
Input: please see the following settings, including \
       1) 'root_path', the 'pms_statistic.py' path for extracting target app(s)'s permissions;
       2) 'pms01_result_path', the result saved path for 'pms_statistic.py' with 01 form;
       3) 'target_app_path', the target app(s) path.
Output: score results with different forms.
       1) dict(set) form 
       2) file form
Method: see the score function
       step1: get 01 file permissions of target apk file using 'get_pms' function;
       step2: change the 01 permissions to list form using 'loadDataSet_real' function;
       step3: match the target permissions to baseline permissions and their 'support degree';
       step4: save the results to different forms.       
"""
#setting
root_path = "E:\\experiment\\experiment1\\apkscan"
#pms01_result_path = "E:\\experiment\\experiment1\\apkscan\\output\\Droidbench_permission.txt"
pms01_result_path = "E:\\experiment\\experiment1\\apkscan\\output\\discussions_permission.txt"
#target_app_path = "D:\\app_malware\\samples\\0e63ba4bb6712456e8f9dd79bc0ebb2466b13ce2.apk"
#target_app_path = "E:\\paper\\2014_spring\\android_static_flow\\DroidBench-master\\DroidBench-master\\apk"
target_app_path = "D:\\apks_discussion"
#appname_path = "E:\\experiment\\experiment1\\apkscan\\output\\app_name.txt"
#score_result = "E:\\experiment\\experiment1\\apkscan\\output\\Droidbench_score_result.txt"
score_result = "E:\\experiment\\experiment1\\apkscan\\output\\discussions.txt"


malware01_result = "E:\\experiment\\apriori\\apriori-1.0.0\\apriori-1.0.0\\permission2.txt"
benign01_result = "E:\\experiment\\apriori\\apriori-1.0.0\\apriori-1.0.0\\permission1.txt"



def get_pms(apkscan_path, src, async=False):
	"""
	get permissions of target apk file
	"""
	ret = ""
	 
	info_msg = "get permissions from apk file '%s'" %src
	
	try:
		pms_bin = os.path.join(apkscan_path,'pms_statistic.py')
		if not os.path.exists(pms_bin):
			err_msg = "pms_statistic file is not exists in path[%s]" %apkscan_path
			#logger.error(err_msg)
			return err_msg
		if True == os.path.isdir(src):
			cmd = 'python %s -p "%s"' %(pms_bin, src)
			print "This is a score for 'a path' that includes many apps"
		else:
			cmd = 'python %s -a "%s"' %(pms_bin, src)
			print "This is a score for 'single app'"
		
		process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE, close_fds=False)
		out, err = process.communicate()
		if not async:
			process.wait()
		time.sleep(1)
		#ret = conf.pms_result_path
		ret = pms01_result_path
		#name = appname_path #record the name depends on the sequence of 01 file apps
		return ret
	except Exception,e:
		print e
	
	return ret

#----------------------------------------------------------------------
def loadDataSet_real(filePath): 
	"""
	convert general file to data type which can be process
	input: txt file
	format as:
	name1
	1 0 0 0 0 0 1 0 0 0 0 0 0 1 1 1 0 0 0
	name2
	1 0 0 1 0 0 1 0 0 0 0 0 0 1 0 1 0 0 0
	name3
	1 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0
	name4
	1 0 0 0 1 0 1 0 0 0 0 0 0 1 0 0 0 0 0
	name5
	1 0 0 0 0 0 0 0 0 0 0 1 0 1 0 1 0 0 0
	
	output: 
	1)python array
	format as:
	[1, 2,3, 4,6], 
	[2, 3,4, 5,6], 
	[1, 2, 3, 5,6], 
	[1,2,4, 5,6]
	
	2)name array
	"""
	appnames = []
	with open(filePath,'r+') as f:
		list_all = []
		count = 1
		for line in f:	
			if 1==count%2:				
				appnames .append (line)				 
			else:				
				i = 0 #index of all, include empty space
				j = 1 #index of '0' and '1' ,and the index start with "1", not "0"
				list_line = []
				while i < len(line):
					if line[i]=='1':
						list_line.append(j)
						j = j+1
					elif line[i]=='0':
						j = j+1		
					i = i+1
				list_all.append (list_line)
			count= count+1
	return list_all , appnames

def  score(apkscan_path, src, signal=0):
	"""
	computing the score
	"""
	score_ite = 0
	score_all = 0
	path_score_set = {}
	pms01_path = get_pms(apkscan_path,src)
	print pms01_path
	target_pms,appnames = loadDataSet_real(pms01_path)
	set_target_pms =  map(frozenset, target_pms)	
		
	print "\nset_target_pms:" + str(set_target_pms)
	#computing
	supData = get_diff_pms(signal) #seed
	path_name_score_set = {}
	line = len(set_target_pms)-1
	while line >= 0:
		for key in supData:
			score_all = score_all + supData[key]*supData[key]
			if key.issubset(set_target_pms[line]): #Does target_pms contain base feature support 
				score_ite = score_ite + supData[key]*supData[key]
		#print "\nscore_ite:" +str(score_ite)
		score = (score_ite* 1.0000000)/score_all
		appname = appnames[line][:-1]  #using [: -1] delete the last \n 
		print str(score) + " " + appname+"\n"
		#print "score_all: " + str(score_all)+"\n"
		line = line -1
		path_name_score_set[appname]= score
		score_all = 0
		score_ite = 0
	
	with open(score_result,'a+') as f:
		for key in path_name_score_set:
			f.write(key +": " + str(path_name_score_set[key])+"\n")
	return path_name_score_set

#score_real = score("E:\\experiment\\experiment1\\apkscan","D:\\apks\\chengqiang.celever2005.English8900_45666500.apk","E:\\experiment\\experiment1\\apkscan\\output\\permission.txt")

score_real = score(root_path,target_app_path,0)
print score_real 
#pms01_path = get_pms(root_path,target_app_path)
#print pms01_path
