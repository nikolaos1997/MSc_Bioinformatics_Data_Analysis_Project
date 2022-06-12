import win32com
from win32com import client
import glob
from glob import glob






                                     #####################################      Word Doc      #####################################                              

def word_to_pdf(file_path): ### beware...win32com is only working in windows...this is a major limitation!!!

    word = client.DispatchEx("Word.Application") # utylize Word.application from win32 library to parse word documents
    pdf = os.path.splitext(file_path)[0] + ".pdf" # create the pathway to the converted file to be used later
    worddoc = word.Documents.Open(file_path) # open word file
    worddoc.SaveAs(pdf, FileFormat=17) # savev it as pdf , fileformat = 17 is specifically for word documents
    worddoc.Close()
    return pdf #return the pathway to the pdf file, which is saved in the same folder as the word doc



                                             #####################################   PowerPoint Doc  #####################################                              

            
            
def ppt_to_pdf(file_path): # convert to PDF which will used later
    files = glob(file_path)
    powerpoint = win32com.client.Dispatch("Powerpoint.Application") # utylize PowerPoint.application from win32 library to parse word documents
    for filename in files: # go throug the slides
        pdf = os.path.splitext(filename)[0] + ".pdf" # create pathway to the converted file
        deck = powerpoint.Presentations.Open(filename) 
        deck.SaveAs(pdf, formatType = 32) # save the presentation slides as PDF pages
        deck.Close()
    powerpoint.Quit() 
    return pdf # return the pathway of the pdf file



