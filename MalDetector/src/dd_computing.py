import string
import math
'''
Purpose:generate roc data
'''

malScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\PNB\\score_m0.txt"
benScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\PNB\\score_b0.txt"
#malScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\!!score_result_group_m4.txt"
#benScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\!!score_result_group_b4.txt"

#----------------------------------------------------------------------
#def  roc_data_gen(baseline_score):
    #"""
    #generate the ROC data 
    #given a false positive rate, how to get the
    #"""
    #falsePR = 0 
    #truePR = 0
    #malList = convert2list(malScorePath)
    #benList = convert2list(benScorePath)
    #malTotalNum = len(malList)
    #benTotalNum = len(benList)
    #turePositiveNum = 0
    #falsePositiveNum = 0
    
    #for item in malList:
        #if item >= baseline_score:
            #turePositiveNum = turePositiveNum + 1
            
    #for item in benList:
        #if item > baseline_score:
            #falsePositiveNum = falsePositiveNum + 1  
            
    #turePositiveRate = turePositiveNum*1.0000/malTotalNum
    #falsePositiveRate = falsePositiveNum*1.0000/benTotalNum    
    
    #return turePositiveRate , falsePositiveRate        
    
    
def  convert2list(filePath):
    """
    convert the score file to list
    """
    scoreList = []
    with open (filePath,"r+") as f:
        while True:
            tempString = f.readline()
            if tempString:
                startIndex = tempString.rfind(":")
                scoreString = tempString[startIndex+1:-1]
                scoreList.append (string.atof(scoreString))
            else: 
                break
    return scoreList
            
#----------------------------------------------------------------------
def  getExpectation(scoreList):
    """
    get the expectation of score
    """
    totalScore = 0 
    for item in scoreList:
        totalScore += item            
    return totalScore*1.0000/len(scoreList)

def  getVariance(scoreList, expectation):#biao zhun cha
    """
    get the variance of score 
    """
    sq = 0
    for item in scoreList:
        sq += (expectation - item)* (expectation - item)  
    d = sq*1.0000/ len(scoreList)
    
    if (d>=0):
        return math.sqrt (d)
    else:
        return  -1
#----------------------------------------------------------------------

malList = convert2list(malScorePath)
benList = convert2list(benScorePath)

mEx = getExpectation(malList)
bEx = getExpectation(benList)

mDx = getVariance(malList,mEx)
bDx = getVariance(benList,bEx)

if(mDx!=-1 and bDx!=-1):
    DD = (mEx - bEx)/(mDx + bDx)
    print DD
else:
    print "error: below 0 !"






    
        
    