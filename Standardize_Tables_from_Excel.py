import numpy as np
import io
import json
import re
from re import search
from operator import itemgetter
import pathlib
from pathlib import Path
import pandas as pd
from datetime import date 





 ####################################     Excel Doc to BioC JSON      #####################################                              

def excel_to_BioC(file_path, out): # file_path : the path to the Excel file, out : the directory to save BioC JSON file
    
    basename = Path(file_path).stem # get the name of the file from the directory
    

    df = pd.read_excel(file_path, sheet_name = None) # Read excel document

    date1 = str(date.today()) #date of standardization
    documents = []
    bioc_format = {
                "source": "Auto-CORPus (supplementary tables)",
                "date": f'{date1}',
                "key": "autocorpus_supp.key",
                "documents": documents
                   }

    for i,j in enumerate(df.keys()): # iterate through the dictionary of the various tables concerning the various sheets
        sheet = df[j] 
        nump = df[j].to_numpy() # exploit the location of the elements as numpy list
        headings = []#store headings
        content = []#store the values for each heading

        if len(nump) != 0: #sometimes, sheets might be empty

            for k in range(0, len(nump[0])): #iterate through columns of the table
                column_name = nump[0][k] #get headers
         
                column_dic = {
                              "cell_id": F"{i}.{0}.{k}", # get heading location
                              "cell_text":column_name # get heading name
                                }
                headings.append(column_dic)


                for l in range(1, len(nump)):

                    val = nump[l][k]
                    content_dic = {
                                    "cell_id": F"{i}.{l}.{k}", #get values location in the table ## i is the sheet number, l is the row number, k is the column number
                                    "cell_text": val #the value
                                    }
                    content.append(content_dic)

            tableDict = {
                            "inputfile": file_path,
                            "id": F"{l}",   
                            "passages": [
                                {
                                    "infons": {
                                        "section_title_1": "table_title_supp",
                                        "iao_name_1": "document title",
                                        "iao_id_1": "IAO:0000326" # supplmentary information Informaiton Artifact Ontology ID
                                    },
                                    "text": [F"Table {i}", F'{j}']} ## get table number and name of sheet
                                ,{
                                  "infons": {
                                    "section_title_1": "table_caption_supp",
                                    "iao_name_1": "caption",
                                    "iao_id_1": "IAO:0000326"
                                  },
                                  "text": [sheet.columns[0]] #table caption
                                },
                                {
                                  "offset": '',
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
    with open(out + f'\{basename}'+ "_Excel.json", "w+", encoding='utf-8') as outfile:
            json.dump(bioc_format, outfile, ensure_ascii=False, indent=4)
