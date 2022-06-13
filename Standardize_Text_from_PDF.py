import numpy as np
import fitz # PyMuPDF
import io
from re import search
from operator import itemgetter
import glob
from glob import glob
import ntpath
from pathlib import Path



                                        ################################ Standardize Raw Text to BioC JSON ###############################
    
    

def fonts(pdf): # extract word format
   
    styles = {}
    format_count = {}
    
    doc = fitz.open(pdf)

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # block contains text
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        format_id = "{0}".format(s['size'])
                        styles[format_id] = {'size': s['size'], 'font': s['font']}

                        format_count[format_id] = format_count.get(format_id, 0) + 1  # count the fonts usage

    format_count = sorted(format_count.items(), key=itemgetter(1), reverse=True)
    return format_count, styles


def font_tags(format_count, styles): #get dictionary with font sizes as keys and tags as value
   
    para_style = styles[format_count[0][0]]  # get style for most used font by count (paragraph)
    para_size = para_style['size']  # get the paragraph's size

    # sorting the font sizes high to low
    font_sizes = []
    for (font_size, count) in format_count:
        font_sizes.append(float(font_size))
    font_sizes.sort(reverse=True)

    # aggregating the tags for each font size
    idx = 0
    size_tag = {}
    for size in font_sizes:
        idx += 1
        if size == para_size:
            idx = 0
            size_tag[size] = '<p>' # for paragraphs
        if size > para_size:
            size_tag[size] = '<h{0}>'.format(idx) # for headers
        elif size < para_size:
            size_tag[size] = '<s{0}>'.format(idx) # for subscripts, which was not used eventually in the standardization 

    return size_tag


def headers_para(pdf, size_tag): #Scrapes headers & paragraphs from PDF and return texts with element tags.
    
    header_para = []  # list with headers and paragraphs
    first = True  # boolean operator for first header
    previous_s = {}  # previous span
    
    doc = fitz.open(pdf) #PyMuPDF

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # this block contains text

                block_string = ""  # text found in block
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if s['text'].strip():  # removing whitespaces:
                            if first:
                                previous_s = s
                                first = False
                                block_string = size_tag[s['size']] + s['text']
                            else:
                                if s['size'] == previous_s['size']:

                                    if block_string == "":
                                        # new block has started, so append size tag
                                        block_string = size_tag[s['size']] + s['text']
                                    else:  # in the same block, so concatenate strings
                                        block_string += " " + s['text']

                                else:
                                    header_para.append(block_string)
                                    block_string = size_tag[s['size']] + s['text']
                                previous_s = s

                    # new block started, indicating with a pipe
                    block_string += "|"
                header_para.append(block_string)
    return header_para

def text_stand(pdf): 


    f = fonts(pdf)
    head = headers_para(pdf, font_tags(f[0], f[1]))

    clean = []
    for i in head: # clean text from characters that were used to distinguish blocks 
        i = i.replace('-| ', '')
        i = i.replace('|', '')
        i = i.replace('  ', ' ')
        clean.append(i)

     # use the list as reference to detect potential headings in the PDF text
    lista_sup = ['Quality Control','Clinical Perspective ','QA/QC Results','QA/QC Methods','Supplementary Figure','ANIMAL STUDIES','HUMAN STUDIES','Supplemental References','Genotyping Methods','Supplement','Quality Control','Genome wide association genotyping','Supplementary Material','Supporting Methods','Supplementary Methods','References','Supplementary Figure','Study Subjects','Statistical methods','Supplemental Tables','Supplementary Materials','Supplementary Tables','Supplemental Figures','Supplementary Information', 'Electronic supplementary material']
    txt_dic = {} # use the above lista to map the words and detect the tags that are given to the headings in each different pdf
    
    heading_tag_gen = [] #use the heading tag that is found from headings that are included in the lista_sup, to potentially detect heading that are not included in the list
    key_gen = [] # the heading name that will be used as key for the dictionary, with value the text of the paragraph

    for i,j in enumerate(clean): # get heading that are included in the lista_sup
            words = list(j.split())
            if len(words) != 0:
                try:
                    section = words[0] + ' ' + words[1] # use the first words of the splitted text as header names
                except: section = words[0] 
                for k in lista_sup: # iterate through the reference list
                    if search(k.lower(),section.lower()) and words[0].startswith('<'): 
                        heading_tag = words[0][0:4] # that's the heading tag
                        heading_tag_gen.append(heading_tag) # save it for later to detect headings that are not included in the lista_sup
                        try: 
                            key = words[0][3:] + ' ' + words[1] + ' ' + words[2] # the name of the heading that will be used as key to our dictionary
                            key_gen.append(key) # save it for later   
                        except: 
                            key = words[0][3:] + ' ' + words[1]
                            key_gen.append(key)
                        l = []
                        try: 
                            while clean[i+1].startswith('<p>'): # get the paragraph
                                    l.append(clean[i + 1])
                                    i = i + 1
                        except: continue
                        if len(l) != 0:
                            txt_dic[key] = str(l)
                    else:
                        txt_dic['Unrecognized'] = clean
                       
    for i,j in enumerate(clean): # now let's get the headings that are not included in the lista_supp
            words = list(j.split())
            if len(words) != 0:
                if words[0].startswith(str(heading_tag_gen[0])):
                    try: 
                        key = words[0][3:] + ' ' + words[1] + ' ' + words[2]
                    except: 
                        key = words[0][3:] 
                    if key != key_gen[0]: # exclude the headings that are already found
                        l = []
                        try: 
                            while clean[i+1].startswith('<p>'):
                                    l.append(clean[i + 1])
                                    i = i + 1
                        except: continue
                        if len(l) != 0 :
                            txt_dic[key] = str(l)
                

    for key in txt_dic.keys():  
        txt_dic[key] = re.sub('<p>', '',str(txt_dic[key]))
        txt_dic[key] = re.sub('<h0>', '',str(txt_dic[key]))
        txt_dic[key] = re.sub('<h1>', '',str(txt_dic[key]))
        txt_dic[key] = re.sub('<h2>', '',str(txt_dic[key]))
        txt_dic[key] = re.sub('<h3>', '',str(txt_dic[key]))
        txt_dic[key] = re.sub('<s0', '',str(txt_dic[key]))
        txt_dic[key] = re.sub('<s1>', '',str(txt_dic[key]))
        txt_dic[key] = re.sub('<s2>', '',str(txt_dic[key]))
        txt_dic[key] = re.sub('<s3>', '',str(txt_dic[key]))
        
    return txt_dic




def raw_text_to_BioC(txt_dic, file_path, out):
    basename = Path(file_path).stem #get just the name of the file from the directory 
    
    date1 = str(date.today())
    documents = [] #the standardized information
    bioc_format = {
                "source": "Auto-CORPus (supplementary text)",
                "date": f'{date1}',
                "key": "autocorpus_supp.key",
                "infons": {},
                "documents": documents
                   }

    for i in txt_dic.keys():
        content = [txt_dic[i]]

        Dict = {
                        "inputfile": basename,
                        "infons": {},
                        "passages": [
                            {
                                "infons": {
                                    "section_title_1": "section_title_supp",
                                    "iao_name_1": "document title",
                                    "iao_id_1": "IAO:0000326"
                                },
                                "text": [F"{i}"]} # the i indicates the detected header of the paragraph
                            ,
                            {
                              "infons": {
                                "section_title_1": "text_supp",
                                "iao_name_1": "text_supp",
                                "iao_id_1": "IAO:0000326"
                              }, 
                                "data_section": content   
                            }

                        ]
                    }
        documents.append(Dict)
    with open(out + f'\{basename}'+ "_supp_raw_text.json", "w+", encoding='utf-8') as outfile:
        json.dump(bioc_format, outfile, ensure_ascii=False, indent=4)
