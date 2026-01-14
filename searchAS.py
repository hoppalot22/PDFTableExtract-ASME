import os
import PyPDF2
import time
import sys

sys.path.append(r"C:\Users\ahorner\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages")
sys.path.append(r'C:\Users\ahorner\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\Scripts')


from PIL import Image
from pdf2image import convert_from_path
import pytesseract

poppler_path = r"D:\Python\poppler-21.09.0\Library\bin"

#Search term
searchTerm = input("Search Term")

OGtime = time.time()

CURR_DIR = __file__[:-len(os.path.basename(__file__))]

ASpath = r'D:\S32\Boiler Inspection Histories\Inspections 2015-2019\MFC\MFC5 2015\NATA Reports\\'
ASdir = os.listdir(ASpath)
pdfList = []
for file in ASdir:
    if (file[-4:] == '.pdf'):
        pdfList.append(file)
#print (pdfList)
#For testing
#pdfList = pdfList[0:20]

directory = os.listdir(CURR_DIR + r'Junk')

for file in directory:
    os.remove(CURR_DIR + r'Junk\\' + file)

def text_from_pdf(pdf_path):
    img = convert_from_path(pdf_path, dpi = 40, last_page = 1, poppler_path = poppler_path, fmt = 'png', output_folder = CURR_DIR+r"Junk", output_file = "test" + str(time.thread_time()))

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    
    file  = img[0].filename
    
    print(file)
    
    text = pytesseract.image_to_string(Image.open(file)).strip().replace("\n", "")
    
    return text


def getTitle(page1):
    text = page1.extractText()

resultList = []
with open(CURR_DIR + "//results//" + searchTerm + ".txt", 'w+') as file:
    file.writelines("Australian standards that contain the term '" + searchTerm + "':\n\n")
    fails = 0
    located = 0
    for i in range(len(pdfList)):
        contentsFoundFlag = False;
        try:
            with open(ASpath + pdfList[i], 'rb') as text:
                data = PyPDF2.PdfFileReader(text)
                data.decrypt("")
                #print("Searching: " + pdfList[i])
                for j in range(data.numPages):
                    if(j == 0):
                        page1 = data.getPage(j).extractText().lower()
                    page = data.getPage(j).extractText().lower()
                    conIndex = page.find(".......................")
                    if(conIndex<0):
                        if(contentsFoundFlag):
                            break
                        continue
                    contentsFoundFlag = True
                    termIndex = page.find(searchTerm)
                    if(termIndex<0):
                        #print("Term not found")
                        pass
                    else:
                        #print("Located")
                        located += 1
                        if(pdfList[i] not in resultList):                            
                            resultList.append(pdfList[i])                   
                            file.writelines(str(located) + ": " + pdfList[i] + " " + text_from_pdf(ASpath + pdfList[i]) + "\n" + "____________________________________________________"+"\n")
                     
                         
        except:
            #print("Couldn't read document")
            fails += 1
        os.system('cls')
        print(round(i/len(pdfList)*100, 2), "% complete")
        print(round(located/len(pdfList)*100, 2), "% located")
        print(round(fails/len(pdfList)*100, 2), "% failed")
        
print (time.time() - OGtime)
print("All done!")
