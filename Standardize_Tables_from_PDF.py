import numpy as np
import fitz # PyMuPDF
import io
import json
import tabula
from tabula import read_pdf 
import re
from re import search
from operator import itemgetter
import glob
from glob import glob
import ntpath
from pathlib import Path
import camelot
import pandas as pd
from datetime import date






                                             #################### Tables from PDF to BioC JSON #########################
            
            

def get_tables(file): #pdf file  
    tables_cam = camelot.read_pdf(file, pages = 'all' , flavor="stream", split_text=True,strip_text="\n", silent=True)
    lista_cam = [] #camelot library
    for t in range(0, tables_cam.n): # Iterate through all the detected tables    
        tab = tables_cam[t].df # convert to dataframes
        lista_cam.append(tab)


    tables_tab = read_pdf(file, pages = 'all' , encoding = 'latin-1',   stream = True, silent=True, multiple_tables = True) #Tabula
    lista_tab = [] #tabula library
    for t in range(0, len(tables_tab)): # Iterate through all the detected tables    
        tab = pd.DataFrame(tables_tab[t]) # convert into dataframes 
        lista_tab.append(tab)
    return lista_cam, lista_tab


# standardize the identified tables into BioC JSON files
def tab_to_BioC(df_list, file_path, out):
    basename = Path(file_path).stem
    
    date1 = str(date.today())
    documents = []
    bioc_format = {
                "source": "Auto-CORPus (supplementary tables)",
                "date": f'{date1}',
                "key": "autocorpus_supp.key",
                "infons": {},
                "documents": documents
                   }

    for num, df in enumerate(df_list):
        nump = df.to_numpy()
 
        headings = []
        content = []
        try:

            header = [''.join(str(v) for v in nump[0])] #get potential caption
        except: header = ['']
        try:
            for i in range(0, len(nump[0])):
                    column_name = nump[1][i] #get column names
                    if column_name == '': 
                        column_name = nump[2][i]
                    else: 
                        column_name = nump[1][i]
                    column_dic = {
                                  "cell_id": F"{num}.{0}.{i}", # location in the table
                                  "cell_text":column_name
                                    }
                    headings.append(column_dic)
        except: continue
        
        try:
            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    val = df.at[i,j] #get the values
                    content_dic = {
                                        "cell_id": F"{num}.{j}.{i}", 
                                        "cell_text": val
                                        }
                    content.append(content_dic)
        except: 
            for i in range(0, len(nump[0])):
                for j in range(0, len(nump)):
                    val = nump[j][i]
                    content_dic = {
                                        "cell_id": F"{num}.{j}.{i}",
                                        "cell_text": val
                                        }
                    content.append(content_dic)
            
        tableDict = {
                            "inputfile": basename,
                            "id": F"{num}",   # i is the sheet number
                            "infons": {},
                            "passages": [
                                {
                                    "infons": {
                                        "section_title_1": "table_title_supp",
                                        "iao_name_1": "document title",
                                        "iao_id_1": "IAO:0000326"
                                    },
                                    "text": [F"Table {num}"]} # the table number
                                ,{
                                  "infons": {
                                    "section_title_1": "table_caption_supp",
                                    "iao_name_1": "caption",
                                    "iao_id_1": "IAO:0000326"
                                  },
                                  "text": [header]
                                },
                                {
                                  "infons": {
                                    "section_title_1": "table_content_supp",
                                    "iao_name_1": "table",
                                    "iao_id_1": "IAO:0000326"
                                  }, "column_headings": headings,
                                    "data_section": content   
                                }

                            ]
                        }
        documents.append(tableDict)
        #choose a path to place the standardized files
    with open(out + f'\{basename}'+ "_supp_tables.json", "w+", encoding='utf-8') as outfile:
            json.dump(bioc_format, outfile, ensure_ascii=False, indent=4)