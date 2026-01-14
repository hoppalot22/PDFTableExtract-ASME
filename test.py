import sys
import os
import math 

sys.path.append(r"C:\Users\ahorner\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages")
sys.path.append(r'C:\Users\ahorner\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\Scripts')


import pdfminer.high_level
import PyPDF2
#import pydictionary


try:
    draggedFile = sys.argv[1]
except:
    draggedFile = r"D:\Python\Scripts\Searches\CB1-1954 - J Taylor SAI Locked.pdf"

#LaParams = pdfminer.layout.LAParams(all_texts = True, boxes_flow = 0)
with open(draggedFile, 'rb') as fl:
    data = PyPDF2.PdfFileReader(fl)
    data.decrypt("")

numpages = data.getNumPages()
  
for pagenum in range(numpages):
    print(data.getPage(pagenum).extractText().lower())
