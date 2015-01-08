from permission_baseline import PERMISSION_LIST
import operator 
'''
Purpose: Statistic some data features
Methods: 
1)
2)
3)
'''
malware01_result = "E:\\experiment\\apriori\\apriori-1.0.0\\apriori-1.0.0\\permission2.txt"
benign01_result = "E:\\experiment\\apriori\\apriori-1.0.0\\apriori-1.0.0\\permission1.txt"
MALWARENUMBER = 1260
BENIGNNUMBER = 2107
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

#----------------------------------------------------------------------
def  every_pms_percent(filePath,app_number):
	"""
	computing every permission's number percent of whole number of permissions
	"""	
	every_pms_number = []
	every_pms_percent = []
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
	    every_pms_percent.append (item*1.0000/app_number)
	    pms_total_number = pms_total_number + item
	    
	average_pms_number = pms_total_number* 1.0000/app_number
	    
	return every_pms_number,every_pms_percent,average_pms_number
    
#----------------------------------------------------------------------
#----------------------------------------------------------------------
def  same_pms_MtoB(m_file,b_file):
    """
    """
    count = 0
    list_m = loadDataSet_real01(m_file)
    list_b = loadDataSet_real01(b_file)
    
    for item_m in list_m:
	for item_b in list_b:
	    if(str(item_m) == str(item_b)):
		count +=1    
    return count
#----------------------------------------------------------------------------
#def  convert2dict(list143): #list143 is a parameter whose length must be 143
    #"""
    #convert the list result to dictory whose key is PERMISSION NAME.
    #"""
    
    #res_dict_list = [] #return a list whose items are dict
    #i = 0
    #for item in list143:
	#res_dict = {}
	#res_dict[PERMISSION_LIST[i]['Key']] = item	
	#res_dict_list.append (res_dict)
	#i = i+1
    #return res_dict_list
#------------------------------------------------------------------------------------    
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
    

nM,pM,aM = every_pms_percent(malware01_result, MALWARENUMBER)
nB,pB,aB = every_pms_percent(benign01_result, BENIGNNUMBER)

print "number of malware pms: " + str(nM)
print "number of benign pms: " +str(nB)

print "percent of malware pms: " +str(pM)
print "percent of benign pms: " +str(pB)

print "average number of malware pms: " +str(aM)
print "average number of benign pms: " +str(aB)

pM_dict = convert2dict(pM)
print pM_dict
sorted_pM_dict = sorted(pM_dict.iteritems(), key=operator.itemgetter(1), reverse=True) 

pB_dict = convert2dict(pB)
print pB_dict
sorted_pB_dict = sorted(pB_dict.iteritems(), key=operator.itemgetter(1), reverse=True)  
############Computing same permissions app between malwares and benigns ############
same_count = same_pms_MtoB(malware01_result,benign01_result)
print "count of same permissions apps : " + str(same_count)
############Computing distance between malwares and benigns ############
M2B = {}
B2M = {}
for item in pM_dict:
    M2B[item] = pM_dict[item] - pB_dict[item]
    B2M[item] = pB_dict[item] - pM_dict[item]    
sorted_M2B = sorted(M2B.iteritems(), key=operator.itemgetter(1), reverse=True)  
sorted_B2M = sorted(B2M.iteritems(), key=operator.itemgetter(1), reverse=True)  
print "malware minus benign: " + str(sorted_M2B)
print "benign minus malware: " + str(sorted_B2M)

############Function 'sorted' is so important should be remembered!!!############
print sorted_pM_dict
print sorted_pB_dict

with open("E:\\experiment\\experiment1\\apkscan\\output\\data_analysis.txt",'w+') as f:
    f.write("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^sorted_pM_dict:^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
    for item in sorted_pM_dict:
	f.write(str(item) + "\n")
    f.write("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^sorted_pB_dict:^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
    for item in sorted_pB_dict:
	    f.write(str(item) + "\n")    
    f.write("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$malware minus benign:$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")
    for item in sorted_M2B:
	    f.write(str(item) + "\n")    
    f.write("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^benign minus malware:^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
    for item in sorted_B2M:
	    f.write(str(item) + "\n")       
#temp = pM_dict.items()
#temp.reverse()
#pM_dict_sort=[value for key, value in temp]
#pM_dict.reverse ()


#print pM_dict_sort


    
    