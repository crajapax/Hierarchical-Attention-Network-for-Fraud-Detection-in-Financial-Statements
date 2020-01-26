import csv
import requests
import re
import os
import itertools
import unicodedata
from collections import namedtuple
from glob import glob
import requests
import os
import re
import pandas as pd
from nltk.tokenize import RegexpTokenizer, sent_tokenize
import numpy as np


#path to download mda files to 
path="/Volumes/Elements/MasterThesis/Thesis/Data/mda_fraud"
#path="/Volumes/Elements/MasterThesis/Thesis/Data/mda_nofraud"

#create downloadlist file in folder where mdas are being downloaded, see function "downloadMDA"
#creates the downloadlistfile and returns its path
def Downloadlist(filepath,name):
    
    if not os.path.exists(path):
            os.makedirs(path)

    df=pd.read_csv(filepath, sep=',')
    df["filing"]=df.apply(lambda row: row.SECFNAME[11:][:-4].replace("/", "_"), axis=1)
    df2=df[["filing","SECFNAME"]]
    df2.to_csv(path+"/"+ name+".txt", header=None, index=None, sep=",")
    download=path+"/"+ name+".txt"
    return download


def headerclean(temp, temp1):
    mark0=0
    strings1=['</SEC-HEADER>','</IMS-HEADER>']
    hand=open(temp)
    hand.seek(0)
    for x, line in enumerate(hand):
        line=line.strip()
        if any(s in line for s in strings1):
            mark0=x
            break
    hand.seek(0)
    
    newfile=open(temp1,'w')
    for x, line in enumerate(hand):
        if x>mark0:
            newfile.write(line)
    hand.close()
    newfile.close()
    
    newfile=open(temp1,'r')
    hand=open(temp,'w')        
    for line in newfile:
        if "END PRIVACY-ENHANCED MESSAGE" not in line:
            hand.write(line)                
    hand.close()                
    newfile.close()

###########################  XBRL Cleaner  ###################################################

def xbrl_clean(cond1, cond2, str0):
    locations=[0]
    #print locations
    placement1=[]
    str0=str0.lower()
    for m in re.finditer(cond1, str0):
        a=m.start()
        placement1.append(a)
    #print placement1
    
    if placement1!=[]:
        placement2=[]
        for m in re.finditer(cond2, str0):
            a=m.end()
            placement2.append(a)
    #    print placement2
        
        len1=len(placement1)
        placement1.append(len(str0))
        
        for i in range(len1):
            placement3=[]
            locations.append(placement1[i])
            for j in placement2:
                if (j>placement1[i] and j<placement1[i+1]):
                    placement3.append(j)
                    break
            if placement3!=[]:
                locations.append(placement3[0])
            else:
                locations.append(placement1[i])
    
    #print locations
    return locations

###########################  Table Cleaner  ###################################################

def table_clean(cond1, cond2, str1):
    Items0=["item 7", "item7", "item8", "item 8"]
    Items1=["item 1", "item 2","item 3","item 4","item 5","item 6","item 9", "item 10", "item1", "item2","item3","item4","item5","item6","item9", "item10"]
    
    str2=str1.lower()
    placement1=[]
    for m in re.finditer(cond1, str2):
        a=m.start()
        placement1.append(a)
    n=len(placement1)
    placement1.append(len(str2))
    
    placement2=[]
    for m in re.finditer(cond2, str2):
        a=m.end()
        placement2.append(a)
        
    if (placement1!=[] and placement2!=[]):
        current=str1[0:placement1[0]]
        
        for i in range(n):
            begin=placement1[i]
            for j in placement2:
                if j>begin:
                    end=j
                    break
            
            if end=="":
                current=current+str1[begin:placement1[i+1]]
            else:
                str2=""
                str2=str1[begin:end].lower()
                str2=str2.replace("&nbsp;"," ")
                str2=str2.replace("&NBSP;"," ")
                p = re.compile(r'&#\d{1,5};')
                str2=p.sub("",str2)
                p = re.compile(r'&#.{1,5};')
                str2=p.sub("",str2)
                if any(s in str2 for s in Items0):
                    if not any(s in str2 for s in Items1):
                        current=current+str2
                    
                current=current+str1[end:placement1[i+1]]
                end=""
    else:
        current=str1
    return current



    

###############################################################################################
# This section is the actual program
###############################################################################################




def downloadMDA(filepath,name):
    all_data=[]
    extracted_data=[]
    #download="/Volumes/Elements/MasterThesis/Master/Data/mda/downloadlistNoFraudMda.txt"
    download=Downloadlist(filepath,name)
    print(download)
#############################################################################################################
#The are just hosting text files that can be ignored.  You need them to recored the data as the program runs.
#############################################################################################################
    temp=os.path.join(path,"temp.txt")
    temp1=os.path.join(path,"newfile.txt")

#################################################################################
#This is the file that records the number of sections for each respective filing.
#################################################################################
    LOG=os.path.join(path,"DOWNLOADLOG.txt")
    with open(LOG,'w') as f:
        f.write("Filer\tSECTIONS\n")
        f.close()

######## Download the filing ############
    with open(download, 'r') as txtfile:
        reader = csv.reader(txtfile, delimiter=',')
        for line in reader:
            #print line
            FileNUM=line[0].strip()
            Filer=os.path.join(path, str(line[0].strip())+".txt")
            url = 'https://www.sec.gov/Archives/' + line[1].strip()
            with open(temp, 'w') as f:
                f.write(requests.get('%s' % url).content.decode('utf-8'))
            f.close()
            
    
            
            
    ##### Obtain Header Information on Filing ######################        
            
            #parse(temp, Filer)
            headerclean(temp, temp1)
            
    ##### ASCII Section ######################        
            
            with open(temp,'r') as f:
                str1=f.read()
                output=str1
                locations_xbrlbig=xbrl_clean("<type>zip", "</document>", output)
                locations_xbrlbig.append(len(output))
                
                if locations_xbrlbig!=[]:
                    str1=""
                    if len(locations_xbrlbig)%2==0:
                        for i in range(0,len(locations_xbrlbig),2):
                            str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]

            f.close
            output=str1
            locations_xbrlbig=xbrl_clean("<type>graphic", "</document>", output)
            locations_xbrlbig.append(len(output))
            
            if locations_xbrlbig!=[0]:
                str1=""
                if len(locations_xbrlbig)%2==0:
                    for i in range(0,len(locations_xbrlbig),2):
                        str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]
            
            output=str1
            locations_xbrlbig=xbrl_clean("<type>excel", "</document>", output)
            locations_xbrlbig.append(len(output))
            
            if locations_xbrlbig!=[0]:
                str1=""
                if len(locations_xbrlbig)%2==0:
                    for i in range(0,len(locations_xbrlbig),2):
                        str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]
                        
            output=str1
            locations_xbrlbig=xbrl_clean("<type>pdf", "</document>", output)
            locations_xbrlbig.append(len(output))
            
            if locations_xbrlbig!=[0]:
                str1=""
                if len(locations_xbrlbig)%2==0:
                    for i in range(0,len(locations_xbrlbig),2):
                        str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]
            
            output=str1
            locations_xbrlbig=xbrl_clean("<type>xml", "</document>", output)
            locations_xbrlbig.append(len(output))
            
            if locations_xbrlbig!=[0]:
                str1=""
                if len(locations_xbrlbig)%2==0:
                    for i in range(0,len(locations_xbrlbig),2):
                        str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]

            output=str1
            locations_xbrlbig=xbrl_clean("<type>ex", "</document>", output)
            locations_xbrlbig.append(len(output))
            
            if locations_xbrlbig!=[0]:
                str1=""
                if len(locations_xbrlbig)%2==0:
                    for i in range(0,len(locations_xbrlbig),2):
                        str1=str1+output[locations_xbrlbig[i]:locations_xbrlbig[i+1]]
                        
    ######Remove <DIV>, <TR>, <TD>, and <FONT>###########################
                       
            p = re.compile(r'(<DIV.*?>)|(<DIV\n.*?>)|(<DIV\n\r.*?>)|(<DIV\r\n.*?>)|(<DIV.*?\n.*?>)|(<DIV.*?\n\r.*?>)|(<DIV.*?\r\n.*?>)')
            str1=p.sub("",str1)
            p = re.compile(r'(<div.*?>)|(<div\n.*?>)|(<div\n\r.*?>)|(<div\r\n.*?>)|(<div.*?\n.*?>)|(<div.*?\n\r.*?>)|(<div.*?\r\n.*?>)')
            str1=p.sub("",str1)
            p = re.compile(r'(<TD.*?>)|(<TD\n.*?>)|(<TD\n\r.*?>)|(<TD\r\n.*?>)|(<TD.*?\n.*?>)|(<TD.*?\n\r.*?>)|(<TD.*?\r\n.*?>)')
            str1=p.sub("",str1)
            p = re.compile(r'(<td.*?>)|(<td\n.*?>)|(<td\n\r.*?>)|(<td\r\n.*?>)|(<td.*?\n.*?>)|(<td.*?\n\r.*?>)|(<td.*?\r\n.*?>)')
            str1=p.sub("",str1)
            p = re.compile(r'(<TR.*?>)|(<TR\n.*?>)|(<TR\n\r.*?>)|(<TR\r\n.*?>)|(<TR.*?\n.*?>)|(<TR.*?\n\r.*?>)|(<TR.*?\r\n.*?>)')
            str1=p.sub("",str1)
            p = re.compile(r'(<tr.*?>)|(<tr\n.*?>)|(<tr\n\r.*?>)|(<tr\r\n.*?>)|(<tr.*?\n.*?>)|(<tr.*?\n\r.*?>)|(<tr.*?\r\n.*?>)')
            str1=p.sub("",str1)
            p = re.compile(r'(<FONT.*?>)|(<FONT\n.*?>)|(<FONT\n\r.*?>)|(<FONT\r\n.*?>)|(<FONT.*?\n.*?>)|(<FONT.*?\n\r.*?>)|(<FONT.*?\r\n.*?>)')
            str1=p.sub("",str1)
            p = re.compile(r'(<font.*?>)|(<font\n.*?>)|(<font\n\r.*?>)|(<font\r\n.*?>)|(<font.*?\n.*?>)|(<font.*?\n\r.*?>)|(<font.*?\r\n.*?>)')
            str1=p.sub("",str1)
            p = re.compile(r'(<P.*?>)|(<P\n.*?>)|(<P\n\r.*?>)|(<P\r\n.*?>)|(<P.*?\n.*?>)|(<P.*?\n\r.*?>)|(<P.*?\r\n.*?>)')
            str1=p.sub("",str1)
            p = re.compile(r'(<p.*?>)|(<p\n.*?>)|(<p\n\r.*?>)|(<p\r\n.*?>)|(<p.*?\n.*?>)|(<p.*?\n\r.*?>)|(<p.*?\r\n.*?>)')
            str1=p.sub("",str1)
            str1=str1.replace("</DIV>","")
            str1=str1.replace("</div>","")
            str1=str1.replace("</TR>","")
            str1=str1.replace("</tr>","")
            str1=str1.replace("</TD>","")
            str1=str1.replace("</td>","")
            str1=str1.replace("</FONT>","")
            str1=str1.replace("</font>","")
            str1=str1.replace("</P>","")
            str1=str1.replace("</p>","")
            
        ############# Remove XBRL Sections #########################
                        
            output=str1
            locations_xbrlsmall=xbrl_clean("<xbrl", "</xbrl.*>", output)
            locations_xbrlsmall.append(len(output))
                
            if locations_xbrlsmall!=[0]:
                str1=""
                if len(locations_xbrlsmall)%2==0:
                    for i in range(0,len(locations_xbrlsmall),2):
                        str1=str1+output[locations_xbrlsmall[i]:locations_xbrlsmall[i+1]]
                
        ############# Remove Teble Sections #########################

            output1=table_clean('<table','</table>',str1)
                
        ############# Remove Newlines and Carriage Returns #########################

            str1=str1.replace("\r\n"," ")
            p = re.compile(r'<.*?>')
            str1=p.sub("",str1)
                
        ############# Remove '<a' and '<hr' and <sup Sections #########################        
                
            str1=str1.replace("&nbsp;"," ")
            str1=str1.replace("&NBSP;"," ")
            str1=str1.replace("&LT;","LT")
            str1=str1.replace("&#60;","LT")
            str1=str1.replace("&#160;"," ")
            str1=str1.replace("&AMP;","&")
            str1=str1.replace("&amp;","&")
            str1=str1.replace("&#38;","&")
            str1=str1.replace("&APOS;","'")
            str1=str1.replace("&apos;","'")
            str1=str1.replace("&#39;","'")
            str1=str1.replace('&QUOT;','"')
            str1=str1.replace('&quot;','"')
            str1=str1.replace('&#34;','"')
            str1=str1.replace("\t"," ")
            str1=str1.replace("\v","")
            str1=str1.replace("&#149;"," ")
            str1=str1.replace("&#224;","")
            str1=str1.replace("&#145;","")
            str1=str1.replace("&#146;","")
            str1=str1.replace("&#147;","")
            str1=str1.replace("&#148;","")
            str1=str1.replace("&#151;"," ")
            str1=str1.replace("&#153;","") 
            str1=str1.replace("&#111;","")
            str1=str1.replace("&#153;","")
            str1=str1.replace("&#253;","")
            str1=str1.replace("&#8217;","")
            str1=str1.replace("&#32;"," ")
            str1=str1.replace("&#174;","")
            str1=str1.replace("&#167;","")
            str1=str1.replace("&#169;","")
            str1=str1.replace("&#8220;","")
            str1=str1.replace("&#8221;","")
            str1=str1.replace("&rsquo;","")
            str1=str1.replace("&lsquo;","")
            str1=str1.replace("&sbquo;","")
            str1=str1.replace("&bdquo;","")
            str1=str1.replace("&ldquo;","")
            str1=str1.replace("&rdquo;","")
            str1=str1.replace("\'","")
            p = re.compile(r'&#\d{1,5};')
            str1=p.sub("",str1)
            p = re.compile(r'&#.{1,5};')
            str1=p.sub("",str1)
            str1=str1.replace("_"," ")
            str1=str1.replace("and/or","and or")
            str1=str1.replace("-\n"," ")
            p = re.compile(r'\s*-\s*')
            str1=p.sub(" ",str1)
            p = re.compile(r'(-|=)\s*')
            str1=p.sub(" ",str1)
            p = re.compile(r'\s\s*')
            str1=p.sub(" ",str1)
            p = re.compile(r'(\n\s*){3,}')
            str1=p.sub("\n\n",str1)
            p = re.compile(r'<.*?>')
            str1=p.sub("",str1)

        ################################## MD&A Section #####################################################
                
            item7={}
            item7[1]="item 7\. managements discussion and analysis"
            item7[2]="item 7\.managements discussion and analysis"
            item7[3]="item7\. managements discussion and analysis"
            item7[4]="item7\.managements discussion and analysis"
            item7[5]="item 7\. management discussion and analysis"
            item7[6]="item 7\.management discussion and analysis"
            item7[7]="item7\. management discussion and analysis"
            item7[8]="item7\.management discussion and analysis"
            item7[9]="item 7 managements discussion and analysis"
            item7[10]="item 7managements discussion and analysis"
            item7[11]="item7 managements discussion and analysis"
            item7[12]="item7managements discussion and analysis"
            item7[13]="item 7 management discussion and analysis"
            item7[14]="item 7management discussion and analysis"
            item7[15]="item7 management discussion and analysis"
            item7[16]="item7management discussion and analysis"
            item7[17]="item 7: managements discussion and analysis"
            item7[18]="item 7:managements discussion and analysis"
            item7[19]="item7: managements discussion and analysis"
            item7[20]="item7:managements discussion and analysis"
            item7[21]="item 7: management discussion and analysis"
            item7[22]="item 7:management discussion and analysis"
            item7[23]="item7: management discussion and analysis"
            item7[24]="item7:management discussion and analysis"
            item7[25]="managements discussion and analysis and results of operations"

                
                
            item8={}
            item8[1]="item 8\. financial statements"
            item8[2]="item 8\.financial statements"
            item8[3]="item8\. financial statements"
            item8[4]="item8\.financial statements"
            item8[5]="item 8 financial statements"
            item8[6]="item 8financial statements"
            item8[7]="item8 financial statements"
            item8[8]="item8financial statements"
            item8[9]="item 8a\. financial statements"
            item8[10]="item 8a\.financial statements"
            item8[11]="item8a\. financial statements"
            item8[12]="item8a\.financial statements"
            item8[13]="item 8a financial statements"
            item8[14]="item 8afinancial statements"
            item8[15]="item8a financial statements"
            item8[16]="item8afinancial statements"
            item8[17]="item 8\. consolidated financial statements"
            item8[18]="item 8\.consolidated financial statements"
            item8[19]="item8\. consolidated financial statements"
            item8[20]="item8\.consolidated financial statements"
            item8[21]="item 8 consolidated  financial statements"
            item8[22]="item 8consolidated financial statements"
            item8[23]="item8 consolidated  financial statements"
            item8[24]="item8consolidated financial statements"
            item8[25]="item 8a\. consolidated financial statements"
            item8[26]="item 8a\.consolidated financial statements"
            item8[27]="item8a\. consolidated financial statements"
            item8[28]="item8a\.consolidated financial statements"
            item8[29]="item 8a consolidated financial statements"
            item8[30]="item 8aconsolidated financial statements"
            item8[31]="item8a consolidated financial statements"
            item8[32]="item8aconsolidated financial statements"
            item8[33]="item 8\. audited financial statements"
            item8[34]="item 8\.audited financial statements"
            item8[35]="item8\. audited financial statements"
            item8[36]="item8\.audited financial statements"
            item8[37]="item 8 audited financial statements"
            item8[38]="item 8audited financial statements"
            item8[39]="item8 audited financial statements"
            item8[40]="item8audited financial statements"
            item8[41]="item 8: financial statements"
            item8[42]="item 8:financial statements"
            item8[43]="item8: financial statements"
            item8[44]="item8:financial statements"
            item8[45]="item 8: consolidated financial statements"
            item8[46]="item 8:consolidated financial statements"
            item8[47]="item8: consolidated financial statements"
            item8[48]="item8:consolidated financial statements"
            item8[49]="item 8\. consolidate financial statements"

            look={" see ", " refer to ", " included in "," contained in "}
                
            a={}
            c={}
               
            lstr1=str1.lower()
            for j in range(1,26):
                a[j]=[]
                for m in re.finditer(item7[j], lstr1):
                    if not m:
                        break
                    else:
                        substr1=lstr1[m.start()-20:m.start()]
                        if not any(s in substr1 for s in look):   
                            #print substr1
                            b=m.start()
                            a[j].append(b)
            #print i
            
            list1=[]
            for value in a.values():
                for thing1 in value:
                    list1.append(thing1)
            list1.sort()
            list1.append(len(lstr1))
            #print list1
                       
            for j in range(1,50):
                c[j]=[]
                for m in re.finditer(item8[j], lstr1):
                    if not m:
                        break
                    else:
                        substr1=lstr1[m.start()-20:m.start()]
                        if not any(s in substr1 for s in look):   
                            #print substr1
                            b=m.start()
                            c[j].append(b)
            list2=[]
            
            for value in c.values():
                #print(value)
                for thing2 in value:
                    list2.append(thing2)
            list2.sort()
            #print(list2)   

            locations={}
            if list2==[]:
                print("NO MD&A")
            else:
                if list1==[]:
                    print("NO MD&A")
                else:
                    for k0 in range(len(list1)):
                        locations[k0]=[]
                        locations[k0].append(list1[k0])
                    for k0 in range(len(locations)):
                        for item in range(len(list2)):
                            if locations[k0][0]<=list2[item]:
                                locations[k0].append(list2[item])
                                break
                        if len(locations[k0])==1:
                            del locations[k0]
                
            if locations=={}:
                with open(LOG,'a') as f:
                    f.write(str(FileNUM)+"\t"+"0\n")
                    f.close()
            else:
                sections=0
                    #str1 is whole sec file
                #print(str1)
                    #locations is a dict containing beginning and end char of str1 were Item7 starts
                #print(locations)

                for k0 in range(len(locations)): 
                    #different sections starting with Item7:
                    substring2=str1[locations[k0][0]:locations[k0][1]]
                    #print(substring2)
                    substring3=substring2.split()
                    #print(len(substring3))
                    if len(substring3)>250:
                        sections=sections+1
                        #print(sections)
                        #print(FileNUM)
                        resultdict = dict()
                        resultdict['filing']=FileNUM[:-4]
                        secfname="edgar/data/"+FileNUM.replace('_',"/")
                        resultdict['SECFNAME'] = secfname+".txt"
                        resultdict['CIK'] =FileNUM.split("_")[0]
                        resultdict['mda_extract']=substring2
                        extracted_data.append(resultdict)
                        with open(Filer,'a') as f:
                            #f.write("\n")
                            f.write(substring2+"\n")
                            f.write("\n")
                            f.close()
                with open(LOG,'a') as f:
                        f.write(str(FileNUM)+"\t"+str(sections)+"\n")
                        f.close()
            print(FileNUM)
            all_data.append("edgar/data/"+FileNUM.replace('_',"/") +".txt")

            
        List2=[k["SECFNAME"] for k in extracted_data]
        #print( all_data)
        #print(List2)
        missingmdaList=list(set(all_data)-set(List2))
        return extracted_data, missingmdaList

#returns extracted data list from a folder (path is path of the folder) with containing data
#where the datafiles have the name of "6494_0000905148-99-000728.txt"
def extract_data(path,name):
    extracted_data=[]
    for file in os.listdir(path):
        resultdict = dict()
        filenameopen = os.path.join(path, file)
        List=[path+ name +".txt",path+"/.DS_Store",path+"/DOWNLOADLOG.txt",path+"/downloadlist.txt",path+"/newfile.txt",path+"/temp.txt"]
        if filenameopen not in List:
            #print(filenameopen)
            resultdict['filing']=file[:-4]
            secfname="edgar/data/"+file.replace('_',"/")
            resultdict['SECFNAME'] = secfname
            resultdict['CIK'] =file.split("_")[0]
            with open(filenameopen,'r', encoding='utf-8',errors="replace") as in_file:
                content = in_file.read()
                resultdict['mda_extract']=content
                extracted_data.append(resultdict)

    return extracted_data



#returns List of missing extracted sec/mda files based on a downloadlist and 
#a extracted data output
#download is the path of the downloadlist file (download=path+"/"+ name+".txt")
def missingList(extracted_data,download):
    all_data=[]
    with open(download, 'r') as txtfile:
        reader = csv.reader(txtfile, delimiter=',')
        for line in reader:
            #print line
            FileNUM=line[0].strip()
            all_data.append("edgar/data/"+FileNUM.replace('_',"/") +".txt")

            
    List=[k["SECFNAME"] for k in extracted_data]
    #print( all_data)
    #print(List2)
    missingmdaList=list(set(all_data)-set(List))
    return missingmdaList



#Edgar Extraction and Analysis
stopWordsFile = '/Volumes/Elements/MasterThesis/CodeThesis/StopWords_Generic.txt'
positiveWordsFile = '/Volumes/Elements/MasterThesis/CodeThesis/PositiveWords.txt'
nagitiveWordsFile = '/Volumes/Elements/MasterThesis/CodeThesis/NegativeWords.txt'
uncertainty_dictionaryFile = '/Volumes/Elements/MasterThesis/CodeThesis/uncertainty_dictionary.txt'
constraining_dictionaryFile = '/Volumes/Elements/MasterThesis/CodeThesis/constraining_dictionary.txt'

# # Section 1.1: Positive score, negative score, polarity score

# Loading stop words dictionary for removing stop words

# In[17]:


with open(stopWordsFile ,'r') as stop_words:
    stopWords = stop_words.read().lower()
stopWordList = stopWords.split('\n')
stopWordList[-1:] = []


# tokenizeing module and filtering tokens using stop words list, removing punctuations

# In[18]:


# Tokenizer
def tokenizer(text):
    text = text.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    filtered_words = list(filter(lambda token: token not in stopWordList, tokens))
    return filtered_words


# In[19]:


# Loading positive words
with open(positiveWordsFile,'r') as posfile:
    positivewords=posfile.read().lower()
positiveWordList=positivewords.split('\n')


# In[20]:


# Loading negative words
with open(nagitiveWordsFile ,'r') as negfile:
    negativeword=negfile.read().lower()
negativeWordList=negativeword.split('\n')


# In[21]:


# Calculating positive score 
def positive_score(text):
    numPosWords = 0
    rawToken = tokenizer(text)
    for word in rawToken:
        if word in positiveWordList:
            numPosWords  += 1
    
    sumPos = numPosWords
    return sumPos


# In[22]:


# Calculating Negative score
def negative_word(text):
    numNegWords=0
    rawToken = tokenizer(text)
    for word in rawToken:
        if word in negativeWordList:
            numNegWords -=1
    sumNeg = numNegWords 
    sumNeg = sumNeg * -1
    return sumNeg


# In[23]:


# Calculating polarity score
def polarity_score(positiveScore, negativeScore):
    pol_score = (positiveScore - negativeScore) / ((positiveScore + negativeScore) + 0.000001)
    return pol_score


# # Section 2 -Analysis of Readability -  Average Sentence Length, percentage of complex words, fog index

# In[24]:


# Calculating Average sentence length 
# It will calculated using formula --- Average Sentence Length = the number of words / the number of sentences
     
def average_sentence_length(text):
    sentence_list = sent_tokenize(text)
    tokens = tokenizer(text)
    totalWordCount = len(tokens)
    totalSentences = len(sentence_list)
    average_sent = 0
    if totalSentences != 0:
        average_sent = totalWordCount / totalSentences
    
    average_sent_length= average_sent
    
    return round(average_sent_length)


# In[25]:


# Calculating percentage of complex word 
# It is calculated using Percentage of Complex words = the number of complex words / the number of words 

def percentage_complex_word(text):
    tokens = tokenizer(text)
    complexWord = 0
    complex_word_percentage = 0
    
    for word in tokens:
        vowels=0
        if word.endswith(('es','ed')):
            pass
        else:
            for w in word:
                if(w=='a' or w=='e' or w=='i' or w=='o' or w=='u'):
                    vowels += 1
            if(vowels > 2):
                complexWord += 1
    if len(tokens) != 0:
        complex_word_percentage = complexWord/len(tokens)
    
    return complex_word_percentage
                        


# In[26]:


# calculating Fog Index 
# Fog index is calculated using -- Fog Index = 0.4 * (Average Sentence Length + Percentage of Complex words)

def fog_index(averageSentenceLength, percentageComplexWord):
    fogIndex = 0.4 * (averageSentenceLength + percentageComplexWord)
    return fogIndex


# # Section 4: Complex word count

# In[27]:


# Counting complex words
def complex_word_count(text):
    tokens = tokenizer(text)
    complexWord = 0
    
    for word in tokens:
        vowels=0
        if word.endswith(('es','ed')):
            pass
        else:
            for w in word:
                if(w=='a' or w=='e' or w=='i' or w=='o' or w=='u'):
                    vowels += 1
            if(vowels > 2):
                complexWord += 1
    return complexWord


# # Section 5: Word count

# In[28]:


#Counting total words

def total_word_count(text):
    tokens = tokenizer(text)
    return len(tokens)


# In[29]:


# calculating uncertainty_score
with open(uncertainty_dictionaryFile ,'r') as uncertain_dict:
    uncertainDict=uncertain_dict.read().lower()
uncertainDictionary = uncertainDict.split('\n')

def uncertainty_score(text):
    uncertainWordnum =0
    rawToken = tokenizer(text)
    for word in rawToken:
        if word in uncertainDictionary:
            uncertainWordnum +=1
    sumUncertainityScore = uncertainWordnum 
    
    return sumUncertainityScore



# In[30]:


# calculating constraining score
with open(constraining_dictionaryFile ,'r') as constraining_dict:
    constrainDict=constraining_dict.read().lower()
constrainDictionary = constrainDict.split('\n')

def constraining_score(text):
    constrainWordnum =0
    rawToken = tokenizer(text)
    for word in rawToken:
        if word in constrainDictionary:
            constrainWordnum +=1
    sumConstrainScore = constrainWordnum 
    
    return sumConstrainScore



# In[31]:


# Calculating positive word proportion

def positive_word_prop(positiveScore,wordcount):
    positive_word_proportion = 0
    if wordcount !=0:
        positive_word_proportion = positiveScore / wordcount
        
    return positive_word_proportion


# In[32]:


# Calculating negative word proportion

def negative_word_prop(negativeScore,wordcount):
    negative_word_proportion = 0
    if wordcount !=0:
        negative_word_proportion = negativeScore / wordcount
        
    return negative_word_proportion


# In[33]:


# Calculating uncertain word proportion

def uncertain_word_prop(uncertainScore,wordcount):
    uncertain_word_proportion = 0
    if wordcount !=0:
        uncertain_word_proportion = uncertainScore / wordcount
        
    return uncertain_word_proportion


# In[34]:


# Calculating constraining word proportion

def constraining_word_prop(constrainingScore,wordcount):
    constraining_word_proportion = 0
    if wordcount !=0:
        constraining_word_proportion = constrainingScore / wordcount
        
    return constraining_word_proportion


# In[35]:


# calculating Constraining words for whole report

def constrain_word_whole(mdaText,qqdmrText,rfText):
    wholeDoc = mdaText + qqdmrText + rfText
    constrainWordnumWhole =0
    rawToken = tokenizer(wholeDoc)
    for word in rawToken:
        if word in constrainDictionary:
            constrainWordnumWhole +=1
    sumConstrainScoreWhole = constrainWordnumWhole 
    
    return sumConstrainScoreWhole


# In[36]:



def TextAnalysis(extracted_data):


    df = pd.DataFrame(extracted_data)
    df['mda_positive_score'] = df.mda_extract.apply(positive_score)
    df['mda_negative_score'] = df.mda_extract.apply(negative_word)
    df['mda_polarity_score'] = np.vectorize(polarity_score)(df['mda_positive_score'],df['mda_negative_score'])
    df['mda_average_sentence_length'] = df.mda_extract.apply(average_sentence_length)
    df['mda_percentage_of_complex_words'] = df.mda_extract.apply(percentage_complex_word)
    df['mda_fog_index'] = np.vectorize(fog_index)(df['mda_average_sentence_length'],df['mda_percentage_of_complex_words'])
    df['mda_complex_word_count']= df.mda_extract.apply(complex_word_count)
    df['mda_word_count'] = df.mda_extract.apply(total_word_count)
    df['mda_uncertainty_score']=df.mda_extract.apply(uncertainty_score)
    df['mda_constraining_score'] = df.mda_extract.apply(constraining_score)
    df['mda_positive_word_proportion'] = np.vectorize(positive_word_prop)(df['mda_positive_score'],df['mda_word_count'])
    df['mda_negative_word_proportion'] = np.vectorize(negative_word_prop)(df['mda_negative_score'],df['mda_word_count'])
    df['mda_uncertainty_word_proportion'] = np.vectorize(uncertain_word_prop)(df['mda_uncertainty_score'],df['mda_word_count'])
    df['mda_constraining_word_proportion'] = np.vectorize(constraining_word_prop)(df['mda_constraining_score'],df['mda_word_count'])

    return df
    


    



