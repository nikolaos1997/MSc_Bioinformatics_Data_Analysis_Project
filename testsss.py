import numpy as np
import fitz # PyMuPDF\n",
import io
from PIL import Image
import json
import tabula
from tabula import read_pdf 
import pytesseract
import cv2
import matplotlib.pyplot as plt
import re
from re import search
from operator import itemgetter
import glob
from glob import glob
import win32com
import ntpath
from pathlib import Path
import camelot
import pandas as pd
from datetime import date



#####################################   PDF   #####################################                              
    
   ###### Get text in images and Tabular data ########

        
#tables from PDF to BioC 

def get_tables(file): #pdf file  
    tables_cam = camelot.read_pdf(file, pages = 'all' , flavor="stream", split_text=True,strip_text="\n", silent=True)
    lista_cam = [] #camelot library
    for t in range(0, tables_cam.n): # Iterate through all the detected tables    
        tab = tables_cam[t].df
        lista_cam.append(tab)


    tables_tab = read_pdf(file, pages = 'all' , encoding = 'latin-1',   stream = True, silent=True, multiple_tables = True) #Tabula
    lista_tab = [] #tabula library
    for t in range(0, len(tables_tab)): # Iterate through all the detected tables    
        tab = pd.DataFrame(tables_tab[t]) # convert into dataframes 
        lista_tab.append(tab)
    return lista_cam, lista_tab


# identified tables from camelot and tabula
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
        #nump
        try:

            header = [''.join(str(v) for v in nump[0])]
        except: header = ['']
        try:
            for i in range(0, len(nump[0])):
                    column_name = nump[1][i]
                    if column_name == '': 
                        column_name = nump[2][i]
                    else: 
                        column_name = nump[1][i]
               # if column_name == 'nan':
                    #column_name = nump[0][i]
                    column_dic = {
                                  "cell_id": F"{num}.{0}.{i}",
                                  "cell_text":column_name
                                    }
                    headings.append(column_dic)
        except: continue
        
        try:

            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    val = df.at[i,j]
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
                            "inputfile": file,
                            "id": F"{num}",   # i is the sheet number
                            "infons": {},
                            "passages": [
                                {
                                    "offset": 0,
                                    "infons": {
                                        "section_title_1": "table_title_supp",
                                        "iao_name_1": "document title",
                                        "iao_id_1": "IAO:0000326"
                                    },
                                    "text": [F"Table {num}"]}
                                ,{
                                  "offset": 1,
                                  "infons": {
                                    "section_title_1": "table_caption_supp",
                                    "iao_name_1": "caption",
                                    "iao_id_1": "IAO:0000326"
                                  },
                                  "text": [header]
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
    with open(out + f'\{basename}'+ "_supp_tables_camelot.json", "w+", encoding='utf-8') as outfile:
            json.dump(bioc_format, outfile, ensure_ascii=False, indent=4)
    

## get text from the images
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" # have this line of code all the time before using pytesseract!!!
 
def image_to_text(pdf):
    pdf_file = fitz.open(pdf)

    image_dic = {} # initialize a dictionary to place the text from each image

    for i, page_index in enumerate(range(len(pdf_file))):  # Iterate through all the pages of the PDF file

        ### GET TABLES
        page = pdf_file[page_index] 

         ### GET TEXT IN IMAGES
        for image_index, img in enumerate(page.get_images(), start=1): # iterate through the potential images in pages
            xref = img[0] # get the XREF of the image
            base_image = pdf_file.extract_image(xref) # extract the image bytes from each image
            image_bytes = base_image["image"]

            # load it to PIL\n",
            image = Image.open(io.BytesIO(image_bytes)) #load the bytes to Python Imaging Library (PIL)
            nparr = np.frombuffer(image_bytes, np.uint8) # create arrays of the bytes using buffer storage

            image1 = cv2.imdecode(nparr, flags = 2) # decode the array with OpenCV
            color = cv2.cvtColor(image1, cv2.COLOR_GRAY2RGB)
            gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY) # convert to grayscale
            thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] # apply threshold to distinguish pixels as background and foreground
            string = pytesseract.image_to_string(thresh) # Use Pytesseract to convert image to string
            string = string.replace("\n"," ") 
            key_img = f"image{page_index+1}_{image_index}"

            if string != '': # In case the image does not include any text
                image_dic[key_img] = string
    return image_dic

def image_to_BioC(image_dic, file_path, out):
    basename = Path(file_path).stem
    
    date1 = str(date.today())
    documents = []
    bioc_format = {
                "source": "Auto-CORPus (supplementary figures)",
                "date": f'{date1}',
                "key": "autocorpus_supp.key",
                "infons": {},
                "documents": documents
                   }

    for i in image_dic.keys():
        content = [image_dic[i]]

        tableDict = {
                        "inputfile": file,
                        "id": "",  
                        "infons": {},
                        "passages": [
                            {
                                "offset": 0,
                                "infons": {
                                    "section_title_1": "figure_title_supp",
                                    "iao_name_1": "document title",
                                    "iao_id_1": "IAO:0000326"
                                },
                                "text": [F"{i}"]}
                            ,{
                              "offset": 1,
                              "infons": {
                                "section_title_1": "figure_caption_supp",
                                "iao_name_1": "figure",
                                "iao_id_1": "IAO:0000326"
                              },
                              "text": ['']
                            },
                            {
                              "offset": '',
                              "infons": {
                                "section_title_1": "figure_supp",
                                "iao_name_1": "figure",
                                "iao_id_1": "IAO:0000326"
                              }, 
                                "data_section": content   
                            }

                        ]
                    }
        documents.append(tableDict)
    with open(out + f'\{basename}'+ "_supp_figures.json", "w+", encoding='utf-8') as outfile:
        json.dump(bioc_format, outfile, ensure_ascii=False, indent=4)
