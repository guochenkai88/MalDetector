# computing group scores using linear model

import os
#import signal
import time
from subprocess import PIPE
from lib.core.subprocessng import Popen
from apriori_mod import get_diff_pms
from lib.core.data import conf
from lib.core.data import paths
import string

malware_pms ="E:\\experiment\\experiment1\\apkscan\\output\\!!malware_permission.txt" 
benign_pms ="E:\\experiment\\experiment1\\apkscan\\output\\!!benign_permission.txt" 

testingPath_m0 ="E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_m0.txt"
trainningPath_m0 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_m0.txt"
testingPath_b0 = "E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_b0.txt"
trainningPath_b0 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_b0.txt"

testingPath_m1 ="E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_m1.txt"
trainningPath_m1 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_m1.txt"
testingPath_b1 = "E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_b1.txt"
trainningPath_b1 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_b1.txt"

testingPath_m2 ="E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_m2.txt"
trainningPath_m2 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_m2.txt"
testingPath_b2 = "E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_b2.txt"
trainningPath_b2 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_b2.txt"

testingPath_m3 ="E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_m3.txt"
trainningPath_m3 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_m3.txt"
testingPath_b3 = "E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_b3.txt"
trainningPath_b3 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_b3.txt"

testingPath_m4 ="E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_m4.txt"
trainningPath_m4 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_m4.txt"
testingPath_b4 = "E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_b4.txt"
trainningPath_b4 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_b4.txt"

testingPath_m5 ="E:\\experiment\\experiment1\\apkscan\\output\\Droidbench_permission.txt"
trainningPath_m5 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_m5.txt"
#testingPath_b5 = "E:\\experiment\\experiment1\\apkscan\\output\\!!testingPath_b5.txt"
#trainningPath_b5 ="E:\\experiment\\experiment1\\apkscan\\output\\!!trainningPath_b5.txt"

score_result = "E:\\experiment\\experiment1\\apkscan\\output\\FAS-L\\new_result_m4_w0-5_sup0-8.txt"

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

#----------------------------------------------------------------------
def  grouping(filePath , reminder , testinggroupPath, trainninggroupPath):
	"""
	grouping all the data as 5 groups so that one of them is handled as testing group, 
	and the others are trainning groups.
	
	Para: 'reminder'--0-4, decide which items are selected to be testinggroup.
	      'testinggroupPath'--The path that testing group 01 saved ,
				  attention: this file not only includes 01 content, but also the appname.
	      'trainninggroupPath'--The path that trainning group 01 saved ,
				    attention: this file only includes 01 content.
	"""
	fileList = []
	with open (filePath , 'r+') as f:
		for item in f:
			fileList.append (item)
		
		for item in range(len(fileList)):	
			if fileList[item].rfind("apk") != -1:
				index = fileList[item].rfind("apk")-5
				num = string.atoi(fileList[item][index:index+4])
				if num %5 == reminder:
					with open (testinggroupPath, "a+") as f:
						f.write(fileList[item] ) #not only includes 01 content, but also the appname
						f.write(fileList[item+1] )
				else:
					with open (trainninggroupPath, "a+") as f:						
						f.write(fileList[item+1] )		
	

def  score(pms01_path, malware01_result, benign01_result, signal=0):
	"""
	computing the score
	"""	
	path_score_set = {}
	#pms01_path = get_pms(apkscan_path,src)
	#print pms01_path
	target_pms,appnames = loadDataSet_real(pms01_path)
	set_target_pms =  map(frozenset, target_pms)	
		
	print "\nset_target_pms:" + str(set_target_pms)
	#computing
	supData = get_diff_pms(signal,malware01_result,benign01_result)
	path_name_score_set = {}
	line = len(set_target_pms)-1
	while line >= 0:
		score_all = 0
		score_ite = 0		
		for key in supData:
			score_all = score_all + supData[key]
			if key.issubset(set_target_pms[line]): #Does target_pms contain base feature support 
				score_ite = score_ite + supData[key]
		#print "\nscore_ite:" +str(score_ite)
		score = (score_ite* 1.0000000)/score_all
		appname = appnames[line][:-1]  #using [: -1] delete the last \n 
		print str(score) + " " + appname+"\n"
		line = line -1
		path_name_score_set[appname]= score
		
	
	with open(score_result,'a+') as f:
		for key in path_name_score_set:
			f.write(key +": " + str(path_name_score_set[key])+"\n")
	return path_name_score_set

#score_real = score("E:\\experiment\\experiment1\\apkscan","D:\\apks\\chengqiang.celever2005.English8900_45666500.apk","E:\\experiment\\experiment1\\apkscan\\output\\permission.txt")

#grouping(malware_pms, 4, testingPath_m4, trainningPath_m4)
#grouping(benign_pms, 4, testingPath_b4, trainningPath_b4)

score_real = score(testingPath_m4,trainningPath_m4,trainningPath_b4,0)
print score_real 