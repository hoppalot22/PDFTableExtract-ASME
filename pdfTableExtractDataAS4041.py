import sys
import os
import pymupdf
import pandas as pd


CURR_DIR = __file__[:-len(os.path.basename(__file__))]
print(CURR_DIR)
try:
    draggedFile = sys.argv[1]
except:
    raise Exception("Script requires a pdf argument")

    
def getTable(page, tableID):
    exceptions = [
    ["ð21Þ\n",""],
    ["Table 1A\n",""],
    ["ASME BPVC.II.D.M-2021\n",""],
    ["Table 1A (Cont'd)\n",""],
    ["…", "..."],
    ["–", "_"],
    ["≤", "<="],
    ["≥", ">="],
    ["SA/NF A","SA/NF_A"],
    ["Cond. & heat exch. tubes SB_234","Cond. & heat exch.tubes \n SB_234"],
    ["33Cr_31Ni_32Fe_1.5Mo_0.6Cu_N","33Cr_31Ni_32Fe_1.5Mo_0.6Cu_N\n"],
    ["â€“", "_"],
    ["â€“", "_"],
    ["â€¦", "..."],
    ["K11500 ...", "K11500\n..."],
    ["K03502 60", "K03502\n60"],
    ["K03502 1", "K03502\n1"],
    ["Normalized <=150","Normalized\n<=150"],
    ["K12437 1","K12437\n1"],
    ["Normalized t <= 35","Normalized\nt <= 35"],
    ["SA/EN 10028_7 X","SA/EN 10028_7\nX"],
    ["X2CrNiMoN17_13_3 ...","X2CrNiMoN17_13_3\n..."],
    ["X2CrNiMoN17_11_2 ...","X2CrNiMoN17_11_2\n..."],
    ["S31703 W","S31703\nW"],
    ["25Cr_7.5Ni_3.5Mo_N_Cu_W ","25Cr_7.5Ni_3.5Mo_N_Cu_W\n"],
    ["Smls. & wld. fittings SA_815","Smls. & wld. fittings\nSA_815"],
    [" Sol. ann.","\nSol. ann."],
    ["\n/\n","/"],
    ["SA/NF_A 36_215 P440NJ4","SA/NF A 36_215\nP440NJ4"],
    ["24Cr_22Ni_6Mo_2W_Cu_N ","24Cr_22Ni_6Mo_2W_Cu_N\n"]
    ]
    rawText = page.get_text()
    exceptionText = page.get_text()
    
    for i, line in enumerate(exceptionText.split("\n")[0:-1]):
        if((len(line) == 8)and((line[0] == "K")or(line[0] == "S"))and(line[7:] =="…")):
            exceptions.append([line[0:7]+"...", line[0:7] + "\n..."])
        if((len(line) > 7)and((line[0] == "K")or(line[0] == "G")or(line[0] == "S"))and(" " in line)and("," not in line)and("SA" not in line)and("." not in line)):
            exceptions.append([line, line[0:6] + "\n" + line[7:]])
        if(("Normalized" in line)and (len(line)>11)):
            exceptions.append([line.replace("≤", "<="), line[0:11]+"\n"+line[12:]])
        if((len(line)>15)and("SA" in line)):
            for i,char in enumerate(line):
                if line[-i] == " ":
                    k = i
                    break
            exceptions.append([line.replace("–","_"), line[0:-k]+"\n"+line[-k+1:]])
    
    
    
    for exception in exceptions:
        exceptionText = exceptionText.replace(exception[0],exception[1])
    linesText = exceptionText.split("\n")[0:-1]
    
    if tableID == 3:   
        columns = ["Line No.","40 DegC","65 DegC","100 DegC","125 DegC","150 DegC","200 DegC","250 DegC","300 DegC","325 DegC","350 DegC","375 DegC","400 DegC","425 DegC","450 DegC","475 DegC", "500 DegC"]
    elif tableID == 4:
        columns = ["Line No.","500 DegC","525 DegC","550 DegC","575 DegC","600 DegC","625 DegC","650 DegC","675 DegC","700 DegC","725 DegC","750 DegC","775 DegC","800 DegC","825 DegC","850 DegC","875 DegC","900 DegC"]
    elif tableID == 1:
        columns = ["Line No.","Nominal Composition","Product Form","Spec. No.","Type/Grade","Alloy Desig./UNS No.","Class/Condition/Temper","Size/Thickness, mm","P-No.","Group No."]
    elif tableID == 2:
        columns = ["Line No.", "Min Tensile Strength, Mpa","Min Yield Strength, Mpa","III","VIII-2","External Pressure Chart No.", "Notes"]

    numcols = len(columns)
    
    for i, line in enumerate(linesText):
        if (line == "1"):
            tableStart = i
            break
    else:
        raise Exception("Page does not seem to contain a table, please ensure start and end page numbers are correct")
    
    try:
        tableText = linesText[tableStart:]
    except UnboundLocalError:
        print (rawText)

    table = pd.DataFrame(columns = columns)
    
    row = []
    for i, entry in enumerate(tableText):
        row.append(entry)
        if((i%numcols == numcols-1)and not(i==0)):
            df2 = pd.DataFrame(columns = columns)
            df2.loc[0] = row
            df2["Line No."] = int(df2["Line No."].iloc[0])
            table = pd.concat([table,df2])
            row = []
    
    return table


#Update this logic per your doc

def Main():

    tableStartpage = 347
    tableEndPage = 437

    tableName = "2A"

    with pymupdf.open(draggedFile) as doc:    
        
        myTable = pd.DataFrame()
        
        print (doc[198].get_text())

        # for i in range(int((tableEndPage-tableStartpage)/4)):
        #     os.system('cls')
        #     print(str(round(i/((tableEndPage-tableStartpage)/4)*100,2)) + "%")
        #     if(i<10000):
        #         index = tableStartpage + i*4
        #         def_table = getTable(doc[index],1)
        #         data_table = getTable(doc[index+1],2)
        #         temp_table1 = getTable(doc[index+2],3)
        #         #temp_table2 = getTable(doc[index+3],4)

        #         result = pd.merge(def_table,data_table, on = "Line No.", how = 'outer')
        #         result = pd.merge(result,temp_table1, on = "Line No.", how = 'outer')
        #         #result = pd.merge(result,temp_table2, on = "Line No.", how = 'outer')

        #         myTable = pd.concat([myTable,result])
        
        # print(myTable[myTable["Line No."] == "35"])
        # myTable.to_csv(CURR_DIR + f"\\Table {tableName}.csv")
            
print("done")

if __name__ == "__main__":
    Main()
