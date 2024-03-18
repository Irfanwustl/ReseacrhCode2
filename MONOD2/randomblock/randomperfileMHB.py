#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import random


# In[2]:



###param####
import sys
bgfile=sys.argv[1] #"/Users/irffanalahi/Research/weekly/for_8_27_20/searchmonodcode/crosscheck/newrightmhb/data/CD19-PBMC-1382.bedgraph_rolled.bedgraph_head"
stdfile=sys.argv[2] #"/Users/irffanalahi/Research/weekly/for_8_27_20/searchmonodcode/crosscheck/newrightmhb/data_monod2_intersected_std/CD19-PBMC-1382.bedgraph_rolled.bedgraph_with_monod2_std_head"
outfile=sys.argv[3] #"testout/habijabi"
maxtryforablock=int(sys.argv[4])    #10
maximumblocklength=int(sys.argv[5]) 

bgfiledf=pd.read_csv(bgfile,sep="\t", header=None)
stdfiledf=pd.read_csv(stdfile,sep="\t", header=None)


# In[3]:


def isValidMHB(bdf,randblockstart,randblockend,maxblock,currentblocklist):
    if isfromsamechrom(bdf,randblockstart,randblockend,maxblock)== True:
        if ismutuallyexclusive(currentblocklist,bdf,randblockstart,randblockend)==True:
            return True
        else:
            #print("overlapped")
            return False
    else:
        return False
        

def ismutuallyexclusive(currentblocklist,bdf,randblockstart,randblockend):
    nbchr=bdf.iloc[randblockstart][0]
    nbstart=bdf.iloc[randblockstart][1]
    nbend=bdf.iloc[randblockend][2]
    
    for i in range(len(currentblocklist)):
        currentblockchr=currentblocklist[i][0]
        currentblockstart=currentblocklist[i][1]
        currentblockend=currentblocklist[i][2]
        
        if currentblockchr==nbchr:
            if nbstart >= currentblockend or nbend<=currentblockstart:
                pass
            else:
                return False
    
    return True







def isfromsamechrom(bdf,randblockstart,randblockend,blocklimit):
  
    if randblockend >=bdf.shape[0]:
        return False
    
    if(bdf.iloc[randblockend][1] - bdf.iloc[randblockstart][1] > blocklimit):
        return False
    
 
    startchr=bdf.iloc[randblockstart][0]
    endchr=bdf.iloc[randblockend][0]  
    if startchr==endchr:
        return True
    else:
        return False


# In[4]:


def fullprocess(bdf,stdf,maxblock,maxtry,oname):
    stddfrunm,stdfcolnum=stdf.shape
    bdfrnum,bdfcolnum=bdf.shape
    
    random.seed(0)
    
    ###############################################
    allrows=[]
    for i in range(stddfrunm):
        currentCpGnum=stdf.iloc[i][2]
        
        
        
        for j in range(maxtry):
            
            randblockstart = random.randint(0, bdfrnum-1)
            randblockend= randblockstart+currentCpGnum-1


            #print(currentCpGnum)
            #print(randblockstart,randblockend)

            if isValidMHB(bdf,randblockstart,randblockend,maxblock,allrows)==True:    
                #print("yes")

                newblock=[bdf.iloc[randblockstart][0],bdf.iloc[randblockstart][1],bdf.iloc[randblockend][2]]
                allrows.append(newblock)

                #print(allrows)
                
                break


    outdf=pd.DataFrame(allrows)
    
    #print(outdf)
    
    outdf.to_csv(oname,sep="\t",index=False,header = False)
   
    


# In[5]:



fullprocess(bgfiledf,stdfiledf,maximumblocklength,maxtryforablock,outfile)

