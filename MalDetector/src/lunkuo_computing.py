import string
import math
'''
Purpose:generate roc data
'''

#malScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\PNB\\score_m0.txt"
#benScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\PNB\\score_b0.txt"

malScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\!!score_result_group_m0.txt"
benScorePath = "E:\\experiment\\experiment1\\apkscan\\output\\!!score_result_group_b0.txt"

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
def  distance_gen(val,scoreList):
    """"""
    distance = 0
    for item in scoreList:
        distance +=  abs(val-item)
    distance = distance*1.0000/len(scoreList)
    
    return distance

#----------------------------------------------------------------------
def  max_gen(a,b):
    """"""
    if a>b:
        return a
    else: 
        return b
    
#----------------------------------------------------------------------
def  lunkuoxishu_gen(dis1,dis2):
    """"""
    return (dis2-dis1)/max_gen(dis1,dis2)
######################################################
malList = convert2list(malScorePath)
benList = convert2list(benScorePath)

single_mal_lunkuo = []
single_ben_lunkuo = []
for item in malList:
    dis_1 = distance_gen(item,malList)
    dis_2 = distance_gen(item,benList)
    single_mal_lunkuo.append ( lunkuoxishu_gen(dis_1,dis_2))
    
for item in benList:
    dis_1 = distance_gen(item,benList)
    dis_2 = distance_gen(item,malList)
    single_ben_lunkuo.append ( lunkuoxishu_gen(dis_1,dis_2))
    
lunkuo_total = 0
for item in single_mal_lunkuo:
    lunkuo_total+=item
    
for item in single_ben_lunkuo:
    lunkuo_total+=item
    
lunkuo_total = lunkuo_total*1.0000/(len(single_mal_lunkuo)+len(single_ben_lunkuo))
print lunkuo_total
    
    
    