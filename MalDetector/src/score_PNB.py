"""
Purpose: a contrast method 'BNB' which uses Basic Native Bayes Model to score the target apps.
"""
import operator 
import math

benign01_result= "E:\\experiment\\experiment1\\apkscan\\output\\PNB\\!!trainningPath_b0.txt"
targetPath = "E:\\experiment\\experiment1\\apkscan\\output\\PNB\\!!testingPath_m0.txt"
result_saved_path = "E:\\experiment\\experiment1\\apkscan\\output\\PNB\\score_m0.txt"
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
	    if len(sita)==1  \
	       or len(sita)==3 \
	       or len(sita)==51 \
	       or len(sita)==16 \
	       or len(sita)==54 \
	       or len(sita)==91 \
	       or len(sita)==59 \
	       or len(sita)==70 \
	       or len(sita)==42 :
		print "an lai guo \n"
		sita.append ((item*1.0000+1)/(app_number+1+2*app_number)) #sita=(sum of 'Xi,m' + a0)/(N+a0+b0).
		                                               #To PNB, 9 most critical permissions are a0=1 b0=2N.
		
	    elif len(sita)==88  \
	       or len(sita)==87 \
	       or len(sita)==63 \
	       or len(sita)==39 \
	       or len(sita)==80 \
	       or len(sita)==18 \
	       or len(sita)==37 \
	       or len(sita)==65 \
	       or len(sita)==94 \
	       or len(sita)==128 \
	       or len(sita)==139 \
	       or len(sita)==91 \
	       or len(sita)==49:
		print "an lai guo 1\n"
		sita.append ((item*1.0000+1)/(app_number+1+app_number))  #sita=(sum of 'Xi,m' + a0)/(N+a0+b0).
		                                                         #To PNB, 17 other critical permissions are a0=1 b0=N.
	    else:		
		sita.append ((item*1.0000+1)/(app_number+1+1))  #sita=(sum of 'Xi,m' + a0)/(N+a0+b0).
		                                                #others are a0=1 b0=1
		
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
	for item in list_all:		
		score_temp =1
		for subitem in item:
		    if subitem != 45 and subitem != 7 and subitem != 139 and subitem != 130 and subitem != 9:
			#delete the item whose sita>50%  
			score_temp = score_temp * sita[subitem-1]		
		score_temp = math.log(score_temp) # score = -ln (score_temp)
		score_all[appnames[i]] = -score_temp
		i = i+1
	return score_all	
				
		
score_BNB_all=score(targetPath)	
print score_BNB_all
with open(result_saved_path,'a+') as f:
    for key in score_BNB_all:
	f.write(key[0 : -1] +": " + str(score_BNB_all[key])+"\n")
 

#nB,sita,aB = get_sita(benign01_result, BENIGNNUMBER)
#print sita

#sita_dict = convert2dict(sita)
#print sita_dict
#sorted_sita_dict = sorted(sita_dict.iteritems(), key=operator.itemgetter(1), reverse=True) 
#print sorted_sita_dict