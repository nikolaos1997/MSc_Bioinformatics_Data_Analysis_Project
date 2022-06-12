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
    
    

def fonts(pdf, granularity=False): # extract word format
   
    styles = {}
    font_counts = {}
    
    doc = fitz.open(pdf)

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # block contains text
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        identifier = "{0}".format(s['size'])
                        styles[identifier] = {'size': s['size'], 'font': s['font']}

                        font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

    font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

    
    return font_counts, styles


def font_tags(font_counts, styles): #get dictionary with font sizes as keys and tags as value
   
    p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
    p_size = p_style['size']  # get the paragraph's size

    # sorting the font sizes high to low
    font_sizes = []
    for (font_size, count) in font_counts:
        font_sizes.append(float(font_size))
    font_sizes.sort(reverse=True)

    # aggregating the tags for each font size
    idx = 0
    size_tag = {}
    for size in font_sizes:
        idx += 1
        if size == p_size:
            idx = 0
            size_tag[size] = '<p>'
        if size > p_size:
            size_tag[size] = '<h{0}>'.format(idx)
        elif size < p_size:
            size_tag[size] = '<s{0}>'.format(idx)

    return size_tag


def headers_para(pdf, size_tag): #Scrapes headers & paragraphs from PDF and return texts with element tags.
    
    header_para = []  # list with headers and paragraphs
    first = True  # boolean operator for first header
    previous_s = {}  # previous span
    
    doc = fitz.open(pdf)

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

                                    if block_string and all((c == "|") for c in block_string):
                                        # block_string only contains pipes
                                        block_string = size_tag[s['size']] + s['text']
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

def text_stand(doc): #standardize text considering the previous


    f = fonts(doc, granularity=False)
    head = headers_para(doc, font_tags(f[0], f[1]))

    clean = []
    for i in head:
        i = i.replace('-| ', '')
        i = i.replace('|', '')
        i = i.replace('  ', ' ')
        clean.append(i)


    #lista = ['Abstract','Introduction','Methods','Method', 'Results', 'Discussion','Conclusion','Conclusions', 'Materials', 'References', 'Reference List', 'Supplementary Material'] ## this can be used for the main text
    lista_sup = ['Quality Control','Clinical Perspective ','QA/QC Results','QA/QC Methods','Supplementary Figure','ANIMAL STUDIES','HUMAN STUDIES','Supplemental References','Genotyping Methods','Supplement','Quality Control','Genome wide association genotyping','Supplementary Material','Supporting Methods','Supplementary Methods','References','Supplementary Figure','Study Subjects','Statistical methods','Supplemental Tables','Supplementary Materials','Supplementary Tables','Supplemental Figures','Supplementary Information', 'Electronic supplementary material']
    txt_dic = {} # use the above lista to map the words and detect the tags that are given to the headings in each different pdf
    
    for i,j in enumerate(clean):
            words = list(j.split())
            if len(words) != 0:
                try:
                    section = words[0] + ' ' + words[1] + ' ' + words[2]
                except: section = words[0] + ' ' + words[1]
                for k in lista:
                    try:
                        if search(k.lower(),section.lower()) and words[0].startswith('<'): 
                            heading_tag = words[0][0:4] 
                            key = words[0][3:] + ' ' + words[1]
                    except: 
                        if search(k.lower(),words[0].lower()) and words[0].startswith('<'): 
                            heading_tag = words[0][0:4] 
                            key = words[0][3:] 
                        try: 
                            key = key + ' ' + words[1] + ' ' + words[2]
                        except: continue
                        l = []
                        try: 
                            while clean[i+1].startswith('<p>') and not clean[i+1].startswith(str(heading_tag)):
                                    l.append(clean[i + 1])#[i + 1])
                                    i = i + 1
                        except: continue
                           
                        txt_dic[key] = str(l)
                    else:
                        txt_dic['Unrecognized'] = clean

    for key in txt_dic.keys():  #substitute tags with ""
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
