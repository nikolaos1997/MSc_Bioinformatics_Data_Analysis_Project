import numpy as np
import fitz # PyMuPDF
import io
from PIL import Image
import json
import pytesseract
import cv2
import re
from re import search
from operator import itemgetter
import glob
from glob import glob
import ntpath
from pathlib import Path
import pandas as pd
from datetime import date 





 #################### Get text from the Images and Standardize to BioC JSON ###############################
        
        
        
        
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
            string = pytesseract.image_to_string(thresh) # Use Pytesseract model to convert image to string
            string = string.replace("\n"," ") 
            key_img = f"image_{page_index+1}_{image_index}"

            if string != '': # In case the image does not include any text
                image_dic[key_img] = string
    return image_dic

def image_to_BioC(image_dic, file_path, out):
    basename = Path(file_path).stem #get just the name of the file from the directory 
    
    date1 = str(date.today())
    documents = [] #the standardized information
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
                        "infons": {},
                        "passages": [
                            {
                                "infons": {
                                    "section_title_1": "figure_title_supp",
                                    "iao_name_1": "document title",
                                    "iao_id_1": "IAO:0000326"
                                },
                                "text": [F"{i}"]} # the i indicates the page where the image was found, as well as the number of images in a specific page
                            ,{
                              "infons": {
                                "section_title_1": "figure_caption_supp",
                                "iao_name_1": "figure",
                                "iao_id_1": "IAO:0000326"
                              }
                            },
                            {
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