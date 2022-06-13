from collections import defaultdict
import pandas as pd
from tqdm import tqdm
import json
import os

df = pd.read_excel (r"C:....\SNPs.xlsx") # # the excel file that contains the SNPs extracted from GWAS Central for the publications that the standardization pipelines were applied on.
df = df[['dbSNP_markerID', 'PMID']]


def ent_mapping(text, df = df):# SNP entity detection function
    num = df.to_dict('list') 
    mapper = []
    new_dbSNP_markerID = []
    new_counter = {}
    for i in num.keys():
        counter = {}
        counter[i] = 0
        
        for j in range(0, len(num[i])):
            if str(num[i][j]) in text and num[i][j - 1] != num[i][j]:
                counter[i] +=1
            for k in text.split():
                if k.startswith('rs') and k != num[i][j]:
                    new_dbSNP_markerID.append(k)
                    
        new_counter['new_dbSNP_markerID'] = len(list(dict.fromkeys(new_dbSNP_markerID))) # get the sum of the dbSNPs not included in the GWAS Central        
        mapper.append(counter)
    mapper.append(new_counter)
    return mapper

def mine(file): #iterate through the keys of the BioC JSON, get the standardized text and the section IAO
    # get PMC to compare with its sup file
    jo = json.load(file)

    mine = []
    passages = jo['documents'][0]['passages'] 
    for j in range(0, len(passages)):
        for k in passages[j].keys():
            trial = passages[j][k]
            if type(trial) != int and type(trial) != list:
                mine.append(trial)
    
                    
    resultsaa = []   # apply the mapping function to each section of the standardized file (introduction, methods, results, conclusion), and get the SNP counting for each
    for i, j in tqdm(enumerate(mine)):
        results = {}

        if type(j) != dict:
            res = ent_mapping(j)
            results[mine[i-1]['iao_id_1'] ] = res

            cleaned = {} #remove duplicated empty keys 
            for i in results.keys():
                for j in results[i]:
                    for k in j.keys():
                        if j[k] != 0:
                            cleaned[i] = results[i] 
                            resultsaa.append(cleaned)
                            
    dd = defaultdict(list)
    for d in resultsaa:
        for key, value in d.items():
            dd[key].append(value)
    
    diction = {} # merge the findings from the same sections together, since there can be more than one key from the same section
    for i in dd.keys():
        dic = {}
        list_ = []
        for j in dd[i]:
            for k in j:
                list_.append(k)
        dd1 = defaultdict(list)    
        for l in list_:
            for key, value in l.items():
                dd1[key].append(value)
        for t in dd1:
            dic[t] = sum(dd1[t])
        diction[i] = dic

    return diction
                    
## path  = path to the folder with BioC JSON files
  
os.chdir(path)
  
# iterate through all file
r = {}

for file in os.listdir():
    file_name = file[0:10]
    file_ = open(file, 'r', encoding='utf-8')
    r[file_name] = mine(file_)