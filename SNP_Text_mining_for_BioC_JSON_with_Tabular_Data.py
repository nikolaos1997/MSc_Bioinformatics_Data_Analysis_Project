############TEXT MINING FOR TABLES 

import os
import ntpath
import pandas as pd
from tqdm import tqdm
import json
import collections
import numpy as np




df = pd.read_excel (r"C:.....\SNPs.xlsx") # the excel file that contains the SNPs extracted from GWAS Central for the publications that the standardization pipelines were applied on.
df = df[['dbSNP_markerID', 'PMID']]

def ent_mapping(text, df = df): # SNP entity detection function 
    
    num = df.to_dict('list') 
    mapper = []
    new_counter = {}
    for i in num.keys():
        new_dbSNP_markerID = []
        dbSNP_markerID = []
        counter = {}
        counter[i] = 0
        
        for j in range(0, len(num[i])):
            if str(num[i][j]) in text and num[i][j - 1] != num[i][j]:
                counter[i] +=1
                if num[i][j].startswith('rs'): dbSNP_markerID.append(num[i][j])
            for k in text.split():
                if k.startswith('rs') and k not in num['dbSNP_markerID']:                   
                    new_dbSNP_markerID.append(k)     
        new_counter['new_dbSNP_markerID'] = len(list(dict.fromkeys(new_dbSNP_markerID))) # get the sum of the dbSNPs not included in the GWAS Central        
        mapper.append(counter)
    mapper.append(new_counter)
    return mapper


def merge_dicts_tab(dicts): # merge the findings from all the sections of the table : table caption, content , footer - we could distinguish the number of detected SNP for each section as well but wouldn't give much insights
    dic = {}
    res = collections.defaultdict(list)
    for d in dicts:
        for s in d.keys():
            for l in d[s]:
                for k, v in l.items():
                    res[k].append(v)
    for i in res:
        dic[i] = sum(res[i])
    return dic

def stand_table(file): #iterate through the BioC JSON file and get the standardized text for SNP mining 
    jo = json.load(file)

    mine = [] #place only the standardized text to a list, not keys or other info from the files
    for d in range(0, len(jo['documents'])):
        junior_mine = []
        passages = jo['documents'][d]['passages'] 
        for j in range(0, len(passages)):
            for k in passages[j].keys():
                trial = passages[j][k]
                if type(trial) != int:
                    junior_mine.append(trial)
        mine.append(junior_mine)

    new_mine = [] # this list contains everything 
       #if we want get a specific counting for each section 
    caption = [] # this list contains text from caption 
    footer = [] # this list >> >> from footer
    con = [] # this contains text from the cell values
    for t in range(0, len(mine)):
        mine1 = mine[t]
        new_mine.append(mine1[3]) #table caption
        caption.append(mine1[3])
        for i in mine1[5]: #content
            new_mine.append(i['cell_text']) #headers
            con.append(i['cell_text'])
            
        for i in mine1[6]:  
            for j in i['data_rows']:
                for k in j:
                    new_mine.append(k['cell_text']) #content
                    con.append(k['cell_text'])
        try:
            new_mine.append(mine1[8]) # potential table footer if standardized
            footer.append(mine1[8])
        except: continue
        

    resultsaa_tab = [] #apply the SNP mapping funciton and get the counting for each table
    for i in tqdm(new_mine):
        results = {}
        if i != '' and type(i) != float: 
            results['table'] = ent_mapping(i)

            cleaned = {} # remove the dictionaries that were empty
            for i in results.keys():
                for j in results[i]:
                    for k in j.keys():
                        if j[k] != 0:
                            cleaned[i] = results[i] 
                            resultsaa_tab.append(cleaned)
                            
    return merge_dicts_tab(resultsaa_tab)
    
dic = {} # place the detected SNPs from the GWAS Central
dic_new = {} # place the detected SNPs that were not submitted in GWAS Central


#path = path to the standardized file or folder (BioC JSON)
  
os.chdir(path)
  
# iterate through all file if folder
for file in os.listdir():
    file_name = file[0:10] # get name of the file(PMC ID)
    file_ = open(file, 'r', encoding='utf-8')
    res = stand_table(file_)
    dic[file_name] = res['dbSNP_markerID']
    dic_new[file_name] = res['new_dbSNP_markerID']