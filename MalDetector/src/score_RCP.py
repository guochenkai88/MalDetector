"""
Purpose: a contrast method 'BNB' which uses Basic Native Bayes Model to score the target apps.
"""
import operator 
import math

benign01_result= "E:\\experiment\\experiment1\\apkscan\\output\\!!permission1.txt"
targetPath = "E:\\experiment\\experiment1\\apkscan\\output\\!!permission2.txt"
result_saved_path = "E:\\experiment\\experiment1\\apkscan\\output\\RCP\\Roc_RCP.txt"
BENIGNNUMBER = 1686
NPMS = 143

def loadDataSet_real01(filePath):    #guo
    """
    convert general file to data type which can be process
    input: txt file
    format as:
    1 0 0 0 0 0 1 0 0 0 0 0 0 1 1 1 0 0 0
    1 0 0 1 0 0 1 0 0 0 0 0 0 1 0 1 0 0 0
    1 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0
    1 0 0 0 1 0 1 0 0 0 0 0 0 1 0 0 0 0 0
    1 0 0 0 0 0 0 0 0 0 0 1 0 1 0 1 0 0 0
    
    output: python array
    format as:
    [1, 2,3, 4,6], 
    [2, 3,4, 5,6], 
    [1, 2, 3, 5,6], 
    [1,2,4, 5,6]
    """
    
    with open(filePath,'r+') as f:
	list_all = []
	for line in f:	
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
    return list_all 
#-----------------------------------------------
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
#------------------------------------------------------
def  convert2dict(list143): #list143 is a parameter whose length must be 143
    """
    convert the list result to dictory whose key is PERMISSION NAME.
    """
    res_dict = {}
    #res_dict_list = [] #return a list whose items are dict
    i = 0
    for item in list143:	
	res_dict[PERMISSION_LIST[i]['Key']] = item	
	#res_dict_list.append (res_dict)
	i = i+1
    return res_dict 
#----------------------------------------------------------------------
def  RCP_Evaluate(sita1):
    """
    RCP(sita1)>=sita2
    Though setting signal
    RCP(sita1)>=1
    judge if target App is benign or malicious
    """
    critical_per = [1,3,51,53,54,128,129,59,67,66,57,64,65,16,44,70,49,90,91,139,95,138,37,11,12]
    #lack of NFC permission, cause it can not be found in permission_baseline
    # totally, 25 permissions  
    
    list_all = loadDataSet_real01(benign01_result)
    app_number = len(list_all)
    RCP = []
    
    for item2 in critical_per:
	app_has_CP = 0
	for item1 in list_all:	
	    if item1.count(item2) > 0:
		app_has_CP = app_has_CP + 1
	if (app_has_CP*1.0000)/app_number < sita1:
	    RCP.append (item2)
	    
    return RCP

#----------------------------------------------------------------------
def  cal_rate(targetPath,sita1,sita2=1):
    """
    calculate the warning rate and detection rate
    for warning rate, please set the "targetPath" as benigns;
    for detection rate, please set the "targetPath" as malware;
    """
    #list_all = loadDataSet_real01(benign01_result)
    
    list_target = loadDataSet_real01(targetPath)
    
    RCP = RCP_Evaluate (sita1)
    print str(RCP) + "\n"    
    detection_num = 0    
    
    for item1 in list_target :
	count_sita2 = sita2
	for item2 in RCP:
	    if item1.count(item2)> 0:		
		if count_sita2 <= 1:
		    detection_num += 1
		    break
		else:
		    count_sita2 -= 1
    
    rate = (detection_num*1.0000) /len(list_target)
    
    return rate

threshold=0
with open(result_saved_path,'a+') as f:			
    f.write("turePositiveRate    falsePositiveRate\n")  
while threshold < 1:
    rate1 = cal_rate(targetPath,threshold)
    rate2 = cal_rate(benign01_result,threshold)
    
    print "m_rate:" + str(rate1)
    print "b_rate:" + str(rate2)
    
    with open(result_saved_path,'a+') as f:			
	f.write(str(rate1)+" "+str(rate2)+"\n")       
    threshold += 0.01
	    
	
    
