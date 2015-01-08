"""
Purpose: a contrast method 'BNB' which uses Basic Native Bayes Model to score the target apps.
"""
import operator 
import math

benign01_result= "E:\\experiment\\experiment1\\apkscan\\output\\BNB\\!!trainningPath_b0.txt"
targetPath = "E:\\experiment\\experiment1\\apkscan\\output\\BNB\\!!testingPath_m0.txt"
result_saved_path = "E:\\experiment\\experiment1\\apkscan\\output\\BNB\\score_m0.txt"
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
#--------------------------------------------------------
def  get_sita(filePath,app_number):
	"""
	computing every permission's number percent of whole number of permissions
	"""	
	every_pms_number = []
	sita = []
	pms_total_number = 0
	
	init_index = 0
	while init_index < NPMS: #initialize every_pms_number with '0'
		every_pms_number.append (0)
		init_index = init_index +1
	    
	list_all = loadDataSet_real01(filePath)
	#print list_all[0]
	for every_list in list_all:
		#print every_list
		for item in every_list:		    
			every_pms_number.insert(item-1, every_pms_number[item-1] + 1)	
			del(every_pms_number[item])
			
	for item in every_pms_number:
		sita.append ((item*1.0000+1)/(app_number+1+1))  #sita=(sum of 'Xi,m' + a0)/(N+a0+b0).To BNB, both a0 and b0 are 1.
		pms_total_number = pms_total_number + item
	    
	average_pms_number = pms_total_number* 1.0000/app_number
	    
	return every_pms_number,sita,average_pms_number

#----------------------------------------------------------------------
def  score(target01FilePath):
	"""
	score for target apps using BNB
	"""
	list_all, appnames = loadDataSet_real(target01FilePath)
	nB,sita,aB = get_sita(benign01_result, BENIGNNUMBER)	
	
	score_all = {}
	i = 0
	
	list_test1 = [143,139,7,130,45,44]
	list_test2 = [142,138,6,129,44]
	score_temp1 =1
	score_temp2 =1
	for item1 in list_test1:
	    if item1 != 45 and item1 != 7 and item1 != 139 and item1 != 130 and item1 != 9:
		score_temp1 = score_temp1 * sita[item1-1]	
	score_temp1 = math.log(score_temp1) # score = -ln (score_temp)
	print "score_temp1: "+str(score_temp1)
	
	for item2 in list_test2:
	    if item2 != 45 and item2 != 7 and item2 != 139 and item2 != 130 and item2 != 9:
		score_temp2 = score_temp2 * sita[item2-1]
	score_temp2 = math.log(score_temp2) # score = -ln (score_temp)	
	print "score_temp2: "+str(score_temp2)
	    
	#for item in list_all:		
		#score_temp =1
		#for subitem in item:
		    #if subitem != 45 and subitem != 7 and subitem != 139 and subitem != 130 and subitem != 9:
			##delete the item whose sita>50%  
			#score_temp = score_temp * sita[subitem-1]		
		#score_temp = math.log(score_temp) # score = -ln (score_temp)
		#score_all[appnames[i]] = -score_temp
		#i = i+1
	return score_all	
				
		
#score_BNB_all=score(targetPath)	
#print score_BNB_all
#with open(result_saved_path,'a+') as f:
    #for key in score_BNB_all:
	#f.write(key[0 : -1] +": " + str(score_BNB_all[key])+"\n")
 

nB,sita,aB = get_sita(benign01_result, BENIGNNUMBER)
i=1
for item in sita:
    print str(i) +": "+ str(item)
    i+=1

score_BNB_all=score(targetPath)
#sita_dict = convert2dict(sita)
#print sita_dict
#sorted_sita_dict = sorted(sita_dict.iteritems(), key=operator.itemgetter(1), reverse=True) 
#print sorted_sita_dict