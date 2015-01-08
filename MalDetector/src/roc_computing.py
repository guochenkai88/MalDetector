import string
'''
Purpose:generate roc data
'''

#malScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\BNB\\score_m0.txt"
#benScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\BNB\\score_b0.txt"
malScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\FAS-L\\new_result_m4_w0-5_sup0-8.txt"
benScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\FAS-L\\new_result_b4_w0-5_sup0-8.txt"

#resultPath = "E:\\experiment\\experiment1\\apkscan\\output\\ROC\\Roc_linear_4.txt"
resultPath = "E:\\experiment\\experiment1\\apkscan\\output\\ROC\\Roc_fas-l_4_w0-5_sup0-8.txt"

#----------------------------------------------------------------------
def  roc_data_gen(baseline_score):
    """
    generate the ROC data 
    given a false positive rate, how to get the
    """
    falsePR = 0 
    truePR = 0
    malList = convert2list(malScorePath)
    benList = convert2list(benScorePath)
    malTotalNum = len(malList)
    benTotalNum = len(benList)
    turePositiveNum = 0
    falsePositiveNum = 0
    
    for item in malList:
        if item >= baseline_score:
            turePositiveNum = turePositiveNum + 1
            
    for item in benList:
        if item > baseline_score:
            falsePositiveNum = falsePositiveNum + 1  
            
    turePositiveRate = turePositiveNum*1.0000/malTotalNum
    falsePositiveRate = falsePositiveNum*1.0000/benTotalNum    
    
    return turePositiveRate , falsePositiveRate        
    
    
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
def  getHighestScore(scoreList):
    """
    get the highest score of all score
    """
    highestScore = 0 
    for item in scoreList:
        if item > highestScore:
            highestScore = item            
    return highestScore

def  getLowestScore(scoreList):
    """
    get the highest score of all score
    """
    lowestScore = 1
    for item in scoreList:
        if item < lowestScore:
            lowestScore = item            
    return lowestScore
#----------------------------------------------------------------------

malList = convert2list(malScorePath)
benList = convert2list(benScorePath)

#get benign highest score to start with the FalsePositiveRate = 0
highestBenScore = getHighestScore(benList)
baseScore = highestBenScore
count = 100
i = count

print "baseline   turePositiveRate    falsePositiveRate"
with open(resultPath,'a+') as f:			
    f.write("baseline   turePositiveRate    falsePositiveRate\n")    
while  i > 0:
    baseScore = (i*1.00/count)* highestBenScore
    turePositiveRate , falsePositiveRate = roc_data_gen(baseScore)
    #turePositiveRate , falsePositiveRate = roc_data_gen(10)    
    #print "\nbaseline: "+str(baseScore) + "\nturePositiveRate is : " + str(turePositiveRate) + "\nfalsePositiveRate is : " + str(falsePositiveRate)
    print str(baseScore)+" "+str(turePositiveRate)+" "+str(falsePositiveRate)
    
    with open(resultPath,'a+') as f:			
		f.write(str(baseScore)+" "+str(turePositiveRate)+" "+str(falsePositiveRate)+"\n")      
    i = i -1

    

    
        
    