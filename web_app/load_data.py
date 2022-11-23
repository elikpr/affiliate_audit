import pandas as pd

def load_xls(filename):
    xls = pd.ExcelFile(filename) #use r before absolute file path 

    sheetX = xls.parse(0) #2 is the sheet number+1 thus if the file has only 1 sheet write 0 in paranthesis

    var1 = sheetX['Ism_sharifi']

    name_list = list(var1)
    
    return name_list

