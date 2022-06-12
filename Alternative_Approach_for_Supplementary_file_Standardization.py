import ntpath
from pathlib import Path
import fitz
import mammoth
import pandas as pd
import tabula
from tabula import read_pdf 
import sys
import os
import glob
from glob import glob
import win32com.client
from bs4 import BeautifulSoup
import configparser





## PDF convert to HTML

def pdf_to_html(file_path):

    doc = fitz.open(file_path)  # open the pdf
    out = open(file_path + "_converted" + ".html", "wb")  # output for html file
    for num, page in enumerate(doc):  # iterate the document pages
        #page.read_contents()
        if page.rect[0] - page.rect[2] < page.rect[1] - page.rect[3]: ## tables in Landscape format conversion is problematic
            table = tabula.read_pdf(file_path, pages = num + 1, encoding ='latin-1')
            try: # error when page has image - table[0] out of range!!
                if len(table[0]) > 3: 
                    table[0] = table[0].dropna(axis = 0, how = 'all')
                    text = table[0].to_html().encode("utf8")
                else: text = page.get_svg_image().encode("utf8") ## page with table as image to be further analized....
            except: text = page.get_svg_image().encode("utf8")  ## page as image to be further analized with tess..
        else:
            text = page.get_text('html', clip = 'rect-like').encode("utf8")
        out.write(text) 
        out.write(bytes((12,)))  # write page delimiter (form feed 0x0C)
    out.close()
    return out.name
    
## Word doc convert to HTML
    
def docx_to_html(file_path):
    
    doc = open(file_path, 'rb')
    out = open(file_path + "_converted" + ".html", "wb")
    document = mammoth.convert_to_html(doc)
    out.write(document.value.encode('utf8'))
    doc.close()
    out.close()
    return out.name
    
## Excel doc convert to HTML
    
def excel_to_html(file_path):

    out = open(file_path + "_converted" + ".html", "w")
    df = pd.read_excel(file_path,sheet_name = None)
    for key in df:
        html = df[key].to_html()
        out.write(html)
        out.write('Next table-sheet or the end') # Just to distinguish the tables
    out.close()
    return out.name
    
## PowerPoint doc convert to HTML
    
def ppt_to_html(file_path, formatType = 32):
    files = glob(file_path)
    powerpoint = win32com.client.Dispatch("Powerpoint.Application")
    powerpoint.Visible = 1
    for filename in files:
        pdf = os.path.splitext(filename)[0] + ".pdf"
        deck = powerpoint.Presentations.Open(filename)
        deck.SaveAs(pdf, formatType)
        deck.Close()
    powerpoint.Quit() 
    return pdf_to_html(pdf)
    
## Combine all together
    
def convert_format(file_path): #detect the type of the file and apply conversion accordingly
    basename = ntpath.basename(file_path)

    if Path(basename).suffix == '.pdf':
        pdf_to_html(file_path)

    elif Path(basename).suffix == '.xlsx': 
        excel_to_html(file_path)

    elif Path(basename).suffix == '.docx':
        docx_to_html(file_path)

    elif Path(basename).suffix == '.ppt' or Path(basename).suffix == '.pptx':
        ppt_to_html(file_path)

        
######### Clean the HTML file from structural tags that the conversion added ###########


file = open(file_path, 'rb')
out = open(file_path + "html_pretty" + ".html", "w", encoding="utf-8")
tree = BeautifulSoup(file)
good_html = tree.prettify().encode("utf8")
out.write(good_html)
file.close()   

######### We propose Config Parser library to automatically adapt config file templates for each HTML regarding the different patterns of the tags 
    
config = configparser.ConfigParser()
confi.read('config_file.ini')

####### for each key in the config file, substitute the values with the detected tags
####### for this to be done, the HTML file needs to have a clear structure of the tags for each paragraph, table, image that is included
###### Manual inspection is required due to the random structure of the files