#!"C:\Users\ahorner\AppData\Local\Microsoft\WindowsApps\python3.10.exe"

#used in conjunction with INEPT PDF OPENFILE DECRYPTER to crop out watermark (SHHHHH)
#Drag decrypted file onto this script and new pdf will be create in same directory as original

import sys
import os
import math 

print(os.path.dirname(sys.executable))
print(sys.version)

import pdfminer.high_level
import PyPDF2
#import pydictionary

try:
    draggedFile = sys.argv[1]
except:
    draggedFile = r"D:\Python\Scripts\Searches\1210-2010_A2-2015_AH_unlocked.pdf"

#LaParams = pdfminer.layout.LAParams(all_texts = True, boxes_flow = 0)
with open(draggedFile, 'rb') as fl:
    data = PyPDF2.PdfFileReader(fl)
    output = PyPDF2.PdfFileWriter()
    #data.decrypt("")
    
    
    numpages = data.getNumPages()  
    for pagenum in range(numpages):
        page = data.getPage(pagenum)
        page.cropBox.lowerLeft = (30, 842)
        page.cropBox.upperRight = (595, 0)
        output.addPage(page)
        
    with open(draggedFile[0:-4] + "_WMR.pdf" ,"wb") as out_file:
        output.write(out_file)
