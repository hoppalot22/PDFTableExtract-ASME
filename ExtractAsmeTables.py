import sys
import os
import fitz
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import traceback
import tracemalloc

class ASMETable:

    IDtoHeaderMap = {
        "1A": [["Line No.", "Nominal Composition", "Product Form", "Spec. No.", "Type/Grade", "Alloy Desig./UNS No.", "Class/Condition/Temper", "Size/Thickness (mm)"],
               ["Line No.", "P-No.", "Group No.", "Min. Tensile Strength (MPa)", "Min. Yield Strength (MPa)", "I", "III", "VIII-1", "XII", "External Pressure Chart No.", "Notes"],
               ["Line No.","40", "65", "100", "125", "150", "200", "250", "300", "325", "350", "375", "400", "425", "450", "475"],
               ["Line No.", "500", "525", "550", "575", "600", "625", "650", "675", "700", "725", "750", "775", "800", "825", "850", "875", "900"]],
        "1B": [["Line No.", "Nominal Composition", "Product Form", "Spec. No.", "Type/Grade", "Alloy Desig./UNS No.", "Class/Condition/Temper"],
               ["Line No.", "Size/Thickness (mm)", "P-No.", "Min. Tensile Strength (MPa)", "Min. Yield Strength (MPa)", "I", "III", "VIII-1", "XII", "External Pressure Chart No.", "Notes"],
               ["Line No.", "40", "65", "100", "125", "150", "175", "200", "225", "250", "275", "300", "325", "350", "375", "400", "425", "450", "475"],
               ["Line No.", "500", "525", "550", "575", "600", "625", "650", "675", "700", "725", "750", "775", "800", "825", "850", "875", "900"]],
        "2A": [["Line No.", "Nominal Composition", "Product Form", "Spec. No.", "Type/Grade", "Alloy Desig./UNS No.", "Class/Condition/Temper", "Size/Thickness (mm)", "P-No.", "Group No."],
               ["Line No.", "Min. Tensile Strength (MPa)", "Min. Yield Strength (MPa)", "III", "VIII-2", "External Pressure Chart No.", "Notes"],
               ["Line No.", "40", "65", "100", "125", "150", "200", "250", "300", "325", "350", "375", "400", "425", "450", "475", "500"]],
        "2B": [["Line No.", "Nominal Composition", "Product Form", "Spec. No.", "Type/Grade", "Alloy Desig./UNS No.", "Class/Condition/Temper", "Size/Thickness (mm)", "P-No."],
               ["Line No.", "Min. Tensile Strength (MPa)", "Min. Yield Strength (MPa)", "III", "VIII-2", "External Pressure Chart No.", "Notes"],
               ["Line No.", "40", "65", "100", "125", "150", "175", "200", "225", "250", "275", "300", "325", "350", "375", "400", "425"]],
        "Sy": [["Line No.", "Nominal Composition", "Product Form", "Spec. No.", "Type/Grade", "Alloy Desig./UNS No.", "Class/Condition/Temper"],
               ["Line No.", "Size/Thickness (mm)", "Min. Tensile Strength (MPa)", "Min. Yield Strength (MPa)", "Notes"],
               ["Line No.", "40", "65", "100", "125", "150", "175", "200", "225", "250", "275"],
               ["Line No.", "300", "325", "350", "375", "400", "425", "450", "475", "500", "525"],
               ["Line No.", "550", "575", "600", "625", "650", "675", "700", "725", "750", "775", "800", "825", "850", "875", "900"]],
        "Su": [["Line No.", "Nominal Composition", "Product Form", "Spec. No.", "Type/Grade", ],
               ["Line No.", "Alloy Desig./UNS No.", "Class/Condition/Temper", "Size/Thickness (mm)", "Min. Tensile Strength (MPa)"],
               ["Line No.", "40", "100", "150", "200", "250", "300", "325", "350", "375", "400", "425", "450", "475", "500", "525"],
               ["Line No.", "550", "575", "600", "625", "650", "675", "700", "725", "750", "775", "800", "825", "850", "875", "900"]],
    }


    IDtoColPosMap = {
        "1A": [74,92,160,189,228,258,273,335,356,375,415],
        "1B": [74,92,160,189,228,258,273,335,356,375,415],
        "2A": [74,92,160,189,228,258,273,335,356,375,415],
        "2B": [74,92,160,189,228,258,273,335,356,375,415],
    }

    def __repr__(self):
        return self.data.__repr__()
    
    def __init__(self, tableID):
        self.tableID = tableID
        self.TableNumByPage = {}
        self.subTableIndiciesByPage = {}
        self.pageTableData = {}

        headers = [e for sublist in [self.IDtoHeaderMap[self.tableID][0],*[subHeaders[1:] for subHeaders in self.IDtoHeaderMap[self.tableID][1:]]] for e in sublist]
        self.data = pd.DataFrame(columns=headers).set_index("Line No.")

    def ValidatePageText(self, page, debug = False):
        pageText = page.get_text("text").replace("…", "...")
        
        if any(x not in pageText[0:int(len(pageText)*0.1)] for x in ["Table", self.tableID]):
            print(f"Table {self.tableID} not found on page")
            return None
        
        #print(f"{self.tableID} found at position {pageText.index(self.tableID)}")

        headersFound = []
        for headerRows in self.IDtoHeaderMap[self.tableID]:
            headerWords = []
            for header in headerRows:
                headerWords.extend(header.replace("/", " ").replace("(", "").replace(")", "").split(" "))
            for word in headerWords:
                if word not in pageText[0:int(len(pageText))]:
                    headersFound.append(0)
                    break
            else:
                headersFound.append(1)

        if sum(headersFound) == 0:
            print(f"Table {self.tableID} headers not found")
            return None
        elif sum(headersFound) > 1:
            print(f"Warning Multiple possible headers found for Table {self.tableID}")
            return None
        elif sum(headersFound) == 1:
            if debug:
                print(f"Header found for Table {self.tableID}")
            return headersFound.index(True)


    def GetTableLocation(self, pageNum):
        if len(self.pageNumbers) == 0:
            return 0
        else:
            tableNum = self.TableNumByPage[pageNum]
            subTableNum = self.subTableIndiciesByPage[pageNum]
            return tableNum, subTableNum

    def AddPage(self, page, pageNumber: int = None, debug = False):

        headerIndex = self.ValidatePageText(page.page)
        if headerIndex is None:
            return
        else:
            header = self.IDtoHeaderMap[self.tableID][headerIndex]

        pageTable = page
        table = pageTable.GenerateTable(header)

        if table.columns.tolist() != header:
            print(f"Warning: Extracted table columns do not match expected header for Table {self.tableID} on Page {pageNumber+1}")
            print(f"Expected: {header}")
            print(f"Extracted: {table.columns.tolist()}")
            raise Exception(f"Table column mismatch for Table {self.tableID} on Page {pageNumber+1}")
        #pageTable.show_image(title=f"Table {self.tableID} on Page {pageNumber+1}", withLines=True)

        lastValidPage = max(self.subTableIndiciesByPage.keys()) if len(self.subTableIndiciesByPage) > 0 else None

        if lastValidPage is None:
            self.TableNumByPage[pageNumber] = 1
        elif pageNumber - lastValidPage > len(self.IDtoHeaderMap[self.tableID]):
            self.TableNumByPage[pageNumber] = self.TableNumByPage[lastValidPage] + 1
        elif headerIndex < self.subTableIndiciesByPage[lastValidPage]:
            self.TableNumByPage[pageNumber] = self.TableNumByPage[lastValidPage] + 1
        else:
            self.TableNumByPage[pageNumber] = self.TableNumByPage[lastValidPage]        
        self.subTableIndiciesByPage[pageNumber] = headerIndex
        
        try:
            table["Line No."] = (table["Line No."].astype(int) + self.pageTableData[lastValidPage]["Line No."].astype(int).max()*(headerIndex == 0)) if lastValidPage is not None else table["Line No."].astype(int)
            self.pageTableData[pageNumber] = table
            headings = self.data.columns.tolist() + [e for e in table.columns if (e not in self.data.columns)and(e != "Line No.")]

            self.data = self.data.combine_first(table.set_index("Line No."))[headings]
        except Exception as e:
            print(e)
            print(table)
            traceback.print_exc()
            pageTable.show_image()


class PageTable:
    def __init__(self, Page):
        self.page = Page
        self.words = Page.get_text("words", sort = True)
        self.colXs = []
        self.rowYs = []
        self.headerCenters = []
        self.headers = []
        self.df = pd.DataFrame()

    def GetBbox(self):
        headers = ["word", "x0","y0","x1","y1"]
        bboxData = pd.DataFrame()
        for word in self.words:
            bboxData.loc[len(bboxData),headers] = [word[4],word[0],word[1],word[2],word[3]]
        
        bboxData[headers[1:]] = bboxData[headers[1:]].astype(int)
        return bboxData
    
    def MostCommonPositions(self, n = None):

        bboxData = self.GetBbox()
        headers = bboxData.columns[1:]
        modes = pd.DataFrame()

        for var in headers:            
            mode = bboxData.groupby(var).count().sort_values("word", ascending=False)
            if n == None:
                n = len(mode)
            mode = mode.head(n)["word"].sort_index()
            df = pd.DataFrame()
            df[var] = list(mode.index)
            df[var + "_count"] = list(mode)

            newHeaders = list(modes.columns) + [var] + [var + "_count"]

            modes = pd.concat([modes, df], ignore_index=True, axis = 1)
            modes.columns = newHeaders
        return modes
    
    def FindTableHeader(self, headers):

        headerGap = 4
        
        bboxData = self.GetBbox()
        headerWords = []
        for header in headers:
            headerWords.extend(header.replace("/", " ").replace("(", "").replace(")", "").split(" "))

        bboxs = bboxData[bboxData["word"].isin(headerWords)]
        headerY1 = bboxs["y1"].mode().tolist()[0]
        mostCommonSpacing = (bboxs["y1"] - bboxs["y0"]).mean()*1.3
        
        bboxs = bboxData[(bboxData["y1"] <= headerY1) & (bboxData["y1"] >= (headerY1 - mostCommonSpacing))]

        bboxSortX = bboxs.sort_values("x0")
        bboxWords = bboxSortX["word"].tolist()
        boxStartX = bboxSortX["x0"].tolist()
        boxEndX = bboxSortX["x1"].tolist()
        centroids = ((bboxSortX["x0"] + bboxSortX["x1"])/2).tolist()
        centers = [centroids[0]]

        for i, centroid in enumerate(centroids[1:]):

            if all(word not in headerWords for word in bboxWords[i].replace("/", " ").replace("(", "").replace(")", "").replace(",","").split(" ")):
                #print(f"Skipping {bboxWords[i]} not in header words")
                continue
            else:
                #print(f"Adding {bboxWords[i]} to header centers")
                pass

            if (((centroids[i+1] - centroids[i]) > headerGap) and (boxStartX[i+1]-boxEndX[i]) > headerGap):
                centers.append(centroid)
            else:
                centers[-1] += centroid
                centers[-1] /= 2

        #print(f"Header centers: {centers}")

        headerY1 = bboxs["y1"].max()
        headerY0 = bboxs["y0"].min()

        self.headerPos = [headerY0, headerY1]
        self.headerCenters = centers

        return headerY0, headerY1, centers

    def GenerateTableBounds(self, header):       

        minGap = 4
        offsetX = 0
        offsetY = 1

        _, headerY1, centers = self.FindTableHeader(header)  

        bboxData = self.GetBbox()

        #Restrict to only data below header and above the lowest word (Page number)

        bboxData = bboxData[(bboxData["y1"] > headerY1)&(bboxData["y1"] < bboxData["y1"].max()-5) & (~bboxData["word"].isin(["Ferrous", "Nonferrous", "Materials", "(Cont'd)", "ð25Þ"]))]

        # Find x and y regions that do not intersect with any words
        
        xs = np.arange(bboxData["x0"].min()-3, max(max(centers), bboxData["x1"].max())+15).astype(int)
        x0 = bboxData["x0"].to_numpy()
        x1 = (bboxData["x1"]+minGap).to_numpy()

        invalid_maskX = (
            (xs[:, None] > x0[None, :]) &
            (xs[:, None] < x1[None, :])
        ).any(axis=1)

        validX = xs[~invalid_maskX]
        firstColX0 = validX[validX<centers[0]].max()
        firstColX1 = validX[validX>centers[0]].min()
        firstCol = bboxData[(bboxData["x0"] >= firstColX0) & (bboxData["x1"] <= firstColX1)]
        assert type(firstCol) == pd.DataFrame
        validX = validX[validX>=firstColX0]

        ys = np.arange(firstCol["y0"].min()-3, firstCol["y1"].max()+15).astype(int)
        y0 = firstCol["y0"].to_numpy()
        y1 = firstCol["y1"].to_numpy()

        invalid_maskY = (
            (ys[:, None] > y0[None, :]) &
            (ys[:, None] < y1[None, :])
        ).any(axis=1)

        validY = ys[~invalid_maskY]

        assert type(validX) == type(xs)

        #Descretise Regions
        xBounds = validX[[True, *(np.diff(np.diff(validX))!=0), True]]
        yBounds = validY[[True, *(np.diff(np.diff(validY))!=0), True]]
        
        if xBounds.shape[0]%2 == 1:
            xBounds = np.append(xBounds[0]-3, xBounds)
        if yBounds.shape[0]%2 == 1:
            yBounds = np.append(yBounds[0]-3, yBounds)

        meanInnerX = (xBounds[::2] + xBounds[1::2])/2
        meanInnerY = (yBounds[::2] + yBounds[1::2])/2
        
        return meanInnerX, meanInnerY
    
    def GenerateTable(self, header):
        self.headers = header
        colXs, rowYs = self.GenerateTableBounds(header)

        replaceMap = {
            "…": "...",
            "–": "-",
            "≤": "<=",
            "<": "<",
            "Þ": ")",
            "ð": "(",
        }

        self.colXs = sorted(colXs)
        self.rowYs = sorted(rowYs)

        bboxData = self.GetBbox()

        tableData = pd.DataFrame(columns = header)

        for i in range(len(self.rowYs)-1):
            rowData = []
            for j in range(len(self.colXs)-1):
                cellWords = bboxData["word"][(bboxData["x0"] >= self.colXs[j])][bboxData["x1"] <= self.colXs[j+1]][bboxData["y0"] >= self.rowYs[i]][bboxData["y1"] <= self.rowYs[i+1]]
                cellText = " ".join(cellWords)
                cellText = cellText.translate(str.maketrans(replaceMap)).strip()
                rowData.append(cellText)

            try:
                tableData.loc[len(tableData)] = rowData
            except Exception as e:
                print(f"Error adding row data: {rowData}")
                print(tableData.columns)
                print(rowData)
                self.show_image()
                raise e


        self.df = tableData
        return tableData
    
    def show_image(self, title="", withLines = True):
        """Display a pixmap.

        Just to display Pixmap image of "item" - ignore the man behind the curtain.

        Args:
            item: any PyMuPDF object having a "get_pixmap" method.
            title: a string to be used as image title

        Generates an RGB Pixmap from item using a constant DPI and using matplotlib
        to show it inline of the notebook.
        """
        DPI = 150  # use this resolution

        page = self.page
        pix = page.get_pixmap(dpi = DPI)
        img = np.ndarray([pix.h, pix.w, 3], dtype=np.uint8, buffer=pix.samples_mv)

        y0, y1, centers = [*self.headerPos, self.headerCenters]

        rYmax = max(self.rowYs) if len(self.rowYs) > 0 else y1
        rYmin = min(self.rowYs) if len(self.rowYs) > 0 else y0
        cXmax = max(self.colXs) if len(self.colXs) > 0 else 800
        cXmin = min(self.colXs) if len(self.colXs) > 0 else 0

        plt.figure(dpi=DPI)  # set the figure's DPI
        plt.vlines(x = self.colXs, ymin = rYmin, ymax = rYmax)
        plt.vlines(x = centers, ymin = rYmin, ymax = rYmax, colors="red")
        plt.hlines(y = self.rowYs, xmin = cXmin, xmax = cXmax)
        plt.hlines(y = [y0,y1], xmin = cXmin, xmax = cXmax, colors="green")
        #plt.plot(x["x0"], 800-x["x0_count"]*5, linewidth = 1, color = "red")
        plt.title("")  # set title of image
        _ = plt.imshow(img, extent=(0, pix.w * 72 / DPI, pix.h * 72 / DPI, 0))
        plt.show()       


def Main():

    tracemalloc.start()
    prevSize, prevPeak = 0, 0

    CURR_DIR = __file__[:-len(os.path.basename(__file__))]
    print(CURR_DIR)
    try:
        draggedFile = sys.argv[1]
    except:
        raise Exception("Script requires a pdf argument")

    searchStartPage = 600
    searchEndPage = 867
    tables = {
        "1A" : ASMETable("1A"),
        "2A" : ASMETable("1B"),
        "1B" : ASMETable("2A"),
        "2B" : ASMETable("2B"),
        "Su" : ASMETable("Su"),
        "Sy" : ASMETable("Sy")
              }


    with fitz.open(draggedFile) as doc:

        skippedPages = []

        with open(CURR_DIR + "/log.txt", "w") as log:
            for pageNum in range(searchStartPage-1, searchEndPage):
                print(f"Processing page {pageNum+1}")
                page = doc[pageNum]
                for table in tables.values():
                    if table.ValidatePageText(page, debug=True) is not None:
                        print(f"page {pageNum+1} is a valid {table.tableID} candidate")
                        try:
                            pageTable = PageTable(page)
                            table.AddPage(pageTable, pageNum, debug=True)
                            size, peak = tracemalloc.get_traced_memory()
                            print(f"size = {size/1024} Kib, peak = {peak/1024} Kib")
                            if prevPeak != 0 and (peak - prevPeak)/prevPeak > 1:
                                print(f"Warning, large increase in memory useage on page {pageNum+1}")
                                log.write(f"Warning, large increase in memory useage on page {pageNum+1}")
                            
                            tracemalloc.reset_peak()
                            prevSize, prevPeak = size, peak
                        except Exception as e:
                            print(f"Error adding page {pageNum+1} to Table {table.tableID}: {e}, page has been skipped")
                            traceback.print_exc(file = log)
                        

    for table in tables.values():    
        #print(table)
        table.data.to_csv(CURR_DIR + f"\\Table {table.tableID}.csv")
    print(f"Following Pages contained a table but could not be processed\n {skippedPages}")

if __name__ == "__main__":
    Main()
