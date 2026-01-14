import sys

sys.path.append(r"C:\Users\ahorner\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages")
sys.path.append(r'C:\Users\ahorner\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\Scripts')

import MySearch.Algorithms as Algs

testword = "account"
searchTerm = "swining"
words = []
with open(r"H:\My Documents\Tools\Python\Scripts\Searches\SearchParagraph.txt", 'r') as data:
    for line in data:
        words.append(line.strip())

scoreSheetLev = []
scoreSheetHam = []
print (Algs.LevDist(testword, "a"))
print (Algs.HammingDist(testword, "a"))


scoreSheetLev = []
scoreSheetHam = []
# for word in words:
    # scoreSheetLev.append(Algs.LevDist(searchTerm, word))
# print ("Lev",words[scoreSheetLev.index(min(scoreSheetLev))], min(scoreSheetLev))

for word in words:
    scoreSheetHam.append(Algs.HammingDist(searchTerm, word))
print ("Hamming", words[scoreSheetHam.index(min(scoreSheetHam))], min(scoreSheetHam), "\n")