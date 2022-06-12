import numpy as np
import io
import json
import re
from re import search
from operator import itemgetter
import glob
from glob import glob
import ntpath
from pathlib import Path
import pandas as pd
from datetime import date 





 ####################################     Excel Doc to BioC JSON      #####################################                              

def excel_to_BioC(file_path, out): 
    
    basename = Path(file_path).stem
    

    df = pd.read_excel(file_path, sheet_name = None) # Read excel document

    headings = []
    content = []

    date1 = str(date.today())
    documents = []
    bioc_format = {
                "source": "Auto-CORPus (supplementary tables)",
                "date": f'{date1}',
                "key": "autocorpus_supp.key",
                "infons": {},
                "documents": documents
                   }

    for i,j in enumerate(df.keys()): # iterate through the dictionary of the various tables
        sheet = df[j]
        nump = df[j].to_numpy()
        headings = []
        content = []

        s = 1
        if len(nump) != 0:

            for i in range(0, len(nump[0])):
                column_name = nump[0][i] #get headers
         
                column_dic = {
                              "cell_id": F"{s}.{0}.{i}",
                              "cell_text":column_name
                                }
                headings.append(column_dic)


                for l in range(1, len(nump)):

                    val = nump[l][i]
                    content_dic = {
                                    "cell_id": F"{s}.{l}.{i}",
                                    "cell_text": val
                                    }
                    content.append(content_dic)

            tableDict = {
                            "inputfile": file_path,
                            "id": F"{l}",   # l is the sheet number
                            "passages": [
                                {
                                    "infons": {
                                        "section_title_1": "table_title_supp",
                                        "iao_name_1": "document title",
                                        "iao_id_1": "IAO:0000326"
                                    },
                                    "text": [F"Table {i}", F'{j}']} ## get table number and name of sheet
                                ,{
                                  "infons": {
                                    "section_title_1": "table_caption_supp",
                                    "iao_name_1": "caption",
                                    "iao_id_1": "IAO:0000326"
                                  },
                                  "text": [sheet.columns[0]]
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