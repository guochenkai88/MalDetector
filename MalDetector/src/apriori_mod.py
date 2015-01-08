#!/usr/bin/env python
#coding:utf-8
# Author:  guo
# Purpose: input: permissions "0101" file path
#          output: output of 'get_diff_pms' function 
#  
support  =0.8
import operator 

# Created: 05/17/2014
#----------------------------------------------------------------------
mr = "E:\\experiment\\apriori\\apriori-1.0.0\\apriori-1.0.0\\permission2.txt"
br = "E:\\experiment\\apriori\\apriori-1.0.0\\apriori-1.0.0\\permission1.txt"

def loadDataSet_real(filePath):    #guo
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
def  diff_result(supData1,supData2,minSupport):
    """
    The support of malicious minus the benign is the real support which can reflect the character of maliciouos.
    """
    final_supData = {}
    supData = {}
    for key2 in supData2:
	has_same = 0
	for key1 in supData1:
	    if key2==key1:
		supData[key2]=supData2[key2]-0.5*supData1[key1]
		#supData[key2]=supData2[key2]
		#supData[key2]=supData2[key2]-2*supData1[key1]
		#supData[key2]=supData2[key2]-3*supData1[key1]
		#supData[key2]=supData2[key2]-supData1[key1]
		#supData[key2]=supData2[key2]-0.8*supData1[key1]
		#supData[key2]=supData2[key2]-0.2*supData1[key1]
		#supData[key2]=supData2[key2]-0.6*supData1[key1]
		#supData[key2]=supData2[key2]-10*supData1[key1]
		has_same = 1
	if 0==has_same:
	    supData[key2]=supData2[key2]    
	    
    for key in supData :
	if supData [key] > minSupport:
	    final_supData[key] = supData [key]
    return final_supData
	
    
def loadDataSet():   
    return [[1, 2,3, 4,6], [2, 3,4, 5,6], [1, 2, 3, 5,6], [1,2,4, 5,6]]

#gen 1-itemset
def createC1(dataSet):
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])            
    C1.sort()
    return map(frozenset, C1)#use frozen set so we
                            #can use it as a key in a dict    

def scanD(D, Ck, minSupport):
    ssCnt = {}
    for tid in D:
        for can in Ck:
            if can.issubset(tid):
                if not ssCnt.has_key(can): ssCnt[can]=1
                else: ssCnt[can] += 1
    numItems = float(len(D))
    retList = []
    supportData = {}
    ourputSupData = {} #guo
    for key in ssCnt:
        support = ssCnt[key]/numItems
        if support >= minSupport:
            retList.insert(0,key)
	    ourputSupData[key] =  support #guo
        supportData[key] = support
    return retList, supportData ,ourputSupData#guo


def aprioriGen(Lk, k): #creates Ck
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i+1, lenLk): 
            L1 = list(Lk[i])[:k-2]; L2 = list(Lk[j])[:k-2]
            L1.sort(); L2.sort()
	    #print "L1:",L1
	    #print "L2:",L2
	    #compare the first items to avoid duplicate
            if L1==L2: #if first k-2 elements are equal,namely,besides the last item,all the items of the two sets are the same!
                retList.append(Lk[i] | Lk[j]) #set union
    return retList

def apriori(dataSet, minSupport = 0.5):
    C1 = createC1(dataSet)
    D = map(set, dataSet)
    L1, supportData ,ourputSupData= scanD(D, C1, minSupport)#guo
    L = [L1]
    k = 2
    while (len(L[k-2]) > 0):
        Ck = aprioriGen(L[k-2], k)
        Lk, supK,ourputSupK = scanD(D, Ck, minSupport)#scan DB to get Lk#guo
        supportData.update(supK)
	ourputSupData.update(ourputSupK)#guo
        L.append(Lk)
        k += 1
    return L, supportData,ourputSupData#guo


def generateRules(L, supportData, minConf=0.7):  #supportData is a dict coming from scanD
    bigRuleList = []
    for i in range(1, len(L)):#only get the sets with two or more items
        for freqSet in L[i]:
            H1 = [frozenset([item]) for item in freqSet]
            if (i > 1):
                rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList         

def calcConf(freqSet, H, supportData, brl, minConf=0.7):
    prunedH = [] #create new list to return
    for conseq in H:
        conf = supportData[freqSet]/supportData[freqSet-conseq] #calc confidence
        if conf >= minConf: 
            print freqSet-conseq,'-->',conseq,'conf:',conf
            brl.append((freqSet-conseq, conseq, conf))
            prunedH.append(conseq)
    return prunedH

def rulesFromConseq(freqSet, H, supportData, brl, minConf=0.7):
    print "freqSet:",freqSet
    
    Hmp1=calcConf(freqSet, H, supportData, brl, minConf)
    
    m = len(Hmp1[0])
    print "m:",m,"Hmp1 now:",Hmp1
    if (len(freqSet) > (m + 1)): #try further merging
        Hmp1 = aprioriGen(Hmp1, m+1)#create Hm+1 new candidates
	print 'Hmp1:',Hmp1
        Hmp1 = calcConf(freqSet, Hmp1, supportData, brl, minConf)
	print 'Hmp1 after calculate:',Hmp1
        if (len(Hmp1) > 1):    #need at least two sets to merge
            rulesFromConseq(freqSet, Hmp1, supportData, brl, minConf)

#----------------------------------------------------------------------
def  get_diff_pms(signal = 0 ,malware01_result = mr , benign01_result = br):    
    '''
    input 'benign01_result' and 'malware01_result'
    1.extract the frequency items upon 'support degree'
    2.using 'malware frequency items' minus 'benign items',and get diff results
    3.return the diff results using a dict. 'key' is item name, 'value' is the 'support degree'
    4.expressions for some variabilities:
       dataSet1: 'list form' for the 01 file of benign apps; 
       dataSet2: 'list form' for the 01 file of malware apps;
       ourputSupData1: results of frequence items upon 'support degree' of benign apps;
       ourputSupData2: results of frequence items upon 'support degree' of malware apps;
       supData: The return results that diff the frequence items, using benign 'support degrees' minus malware.
    '''
    #dataSet1=loadDataSet_real("E:\\experiment\\apriori\\apriori-1.0.0\\apriori-1.0.0\\permission1.txt")
    dataSet1=loadDataSet_real(benign01_result) 
    L1,supportData1,ourputSupData1=apriori(dataSet1,support)#guo
    #print 'br1:',supportData1#guo
    #print 'benign baseline:',ourputSupData1#guo
    #with open("result.txt",'w+') as f:
	#f.write("++++++++++++++++++++++++++++++++++++benign apps:(support=0.3)++++++++++++++++++++++++++++++++\n")
	#for key in ourputSupData1:
	    #f.write (str(key))
	    #f.write ( ": %f \n" %ourputSupData1[key])
	    
	#f.write("---------------------------------------------------------------------------------------------\n")
	#f.write("Total: " + str(len(ourputSupData1))+"\n")
	#f.write("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
	
    #dataSet2=loadDataSet_real("E:\\experiment\\apriori\\apriori-1.0.0\\apriori-1.0.0\\permission2.txt")
    dataSet2=loadDataSet_real(malware01_result)
    L2,supportData2,ourputSupData2=apriori(dataSet2,support)#guo
    #print 'br1:',supportData2#guo
    #print 'malware baseline:',ourputSupData2#guo
    #with open("result.txt",'a+') as f:
	#f.write("+++++++++++++++++++++++++++++++++++malicious apps:(support=0.3)++++++++++++++++++++++++++++++\n")
	#for key in ourputSupData2:
	    #f.write (str(key))
	    #f.write ( ": %f \n" %ourputSupData2[key])
	    
	#f.write("---------------------------------------------------------------------------------------------\n")
	#f.write("Total: " + str(len(ourputSupData2)) +"\n")
	#f.write("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    if 0==signal:
	supData = diff_result(ourputSupData1,ourputSupData2,support)
    else:
	supData = diff_result(ourputSupData2,ourputSupData1,support)
    #print 'after differring baseline:',ourputSupData2#guo
    #with open("result.txt",'a+') as f:
	#f.write("+++++++++++++++++++++++++ associate malicious and benign ++++++++++++++++++++++++++++++++++++\n")
	#for key in supData:
	    #f.write (str(key))
	    #f.write ( ": %f \n" %supData[key])
	    
	#f.write("---------------------------------------------------------------------------------------------\n")
	#f.write("Total: " + str(len(supData))+"\n")
	#f.write("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    
    ##brl=generateRules(L, supportData,0.7)#guo
    ##print 'brl:',brl#guo
    return supData



#---------------Computing the malware top 2-5 items----------------
dataSet2=loadDataSet_real(mr)
L2,supportData2,ourputSupData2=apriori(dataSet2,0.3)
malSupDict1 = {}
malSupDict2 = {}
malSupDict3 = {}
malSupDict4 = {}
malSupDict5 = {}

for item in ourputSupData2:
    if(len(item)==1):
	malSupDict1[item] = ourputSupData2[item]    
    elif(len(item)==2):
	malSupDict2[item] = ourputSupData2[item]
    elif(len(item)==3):
	malSupDict3[item] = ourputSupData2[item]
    elif(len(item)==4):
	malSupDict4[item] = ourputSupData2[item]
    elif(len(item)==5):
	malSupDict5[item] = ourputSupData2[item]

sorted_malSupDict1 = sorted(malSupDict1.iteritems(), key=operator.itemgetter(1), reverse=True)  	
sorted_malSupDict2 = sorted(malSupDict2.iteritems(), key=operator.itemgetter(1), reverse=True)  
sorted_malSupDict3 = sorted(malSupDict3.iteritems(), key=operator.itemgetter(1), reverse=True)  
sorted_malSupDict4 = sorted(malSupDict4.iteritems(), key=operator.itemgetter(1), reverse=True)  
sorted_malSupDict5 = sorted(malSupDict5.iteritems(), key=operator.itemgetter(1), reverse=True)  

print "mal 1 items: " + str(sorted_malSupDict1)
print "mal 2 items: " + str(sorted_malSupDict2)
print "mal 3 items: " + str(sorted_malSupDict3)
print "mal 4 items: " + str(sorted_malSupDict4)
print "mal 5 items: " + str(sorted_malSupDict5)

print "-------------------------------------------------"
#---------------Computing the benign top 2-5 items----------------
dataSet1=loadDataSet_real(br)
L1,supportData1,ourputSupData1=apriori(dataSet1,0.3)
benSupDict1 = {}
benSupDict2 = {}
benSupDict3 = {}
benSupDict4 = {}
benSupDict5 = {}

for item in ourputSupData1:
    if(len(item)==1):
	benSupDict1[item] = ourputSupData1[item]    
    elif(len(item)==2):
	benSupDict2[item] = ourputSupData1[item]
    elif(len(item)==3):
	benSupDict3[item] = ourputSupData1[item]
    elif(len(item)==4):
	benSupDict4[item] = ourputSupData1[item]
    elif(len(item)==5):
	benSupDict5[item] = ourputSupData1[item]

sorted_benSupDict1 = sorted(benSupDict1.iteritems(), key=operator.itemgetter(1), reverse=True)  	
sorted_benSupDict2 = sorted(benSupDict2.iteritems(), key=operator.itemgetter(1), reverse=True)  
sorted_benSupDict3 = sorted(benSupDict3.iteritems(), key=operator.itemgetter(1), reverse=True)  
sorted_benSupDict4 = sorted(benSupDict4.iteritems(), key=operator.itemgetter(1), reverse=True)  
sorted_benSupDict5 = sorted(benSupDict5.iteritems(), key=operator.itemgetter(1), reverse=True)  

print "ben 1 items: " + str(sorted_benSupDict1)
print "ben 2 items: " + str(sorted_benSupDict2)
print "ben 3 items: " + str(sorted_benSupDict3)
print "ben 4 items: " + str(sorted_benSupDict4)
print "ben 5 items: " + str(sorted_benSupDict5)
#get_diff_pms()



