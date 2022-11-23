import os
import shutil
from typing import List
from similarity_check import RapidFuzz_Levenshtein
from similarity_check import RapidFuzzChoices_Levenshtein
from load_data import load_xls
from models import NameModel, DBModel



def save_file_to_server(uploaded_file, path=".", save_as="default"):
    extension = os.path.splitext(uploaded_file.filename)[-1]
    temp_file = os.path.join(path, save_as + extension)

    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    return temp_file

def list_to_model(fio_list: DBModel, is_list=False) -> NameModel:
    firstname_db, secondname_db, fathername_db = [], [], []
    if not fio_list:
        fio_list = fio_list.fullnames  
    # fio_list = fio_list.fullnames if not is_list else fio_list
    for fio in fio_list:
        text = fio.split(' ')
        secondname, firstname, fathername = text[0], text[1], " ".join(text[2:])
        firstname_db.append(firstname)
        secondname_db.append(secondname)
        fathername_db.append(fathername)
    fio_model = NameModel(fio_db=fio_list, 
                          firstname_db=firstname_db, 
                          lastname_db=secondname_db, 
                          fathername_db=fathername_db)
    return fio_model

def load_db(xls_filename: str, is_list = False) -> NameModel:
    db = load_xls(xls_filename)
    return list_to_model(db, is_list)

def check_father_child_relation(affiliated_fio: str, 
                                names: NameModel, 
                                threshold:int = 70):
    fio_db = names.fio_db
    fathername_db = names.fathername_db
    
    text = affiliated_fio.split(' ')
    candidate_firstname = text[1]
            
    result = RapidFuzzChoices_Levenshtein(candidate_firstname, fathername_db, 20)
    # TODO: add threshold, ignore if similarity score less than threshold 
    ids = [index for fathername, score, index in result if score > threshold]
    result = [fio_db[id] for id in ids]
   
    possible_fos = generate_possible_child(affiliated_fio)

    d = {}
    for fio in possible_fos:
        curr = RapidFuzzChoices_Levenshtein(fio, result, 20)
        curr = [el for el in curr if el[1] >= threshold]
        for fullname, score, _ in curr:
            if fullname not in d:
                d[fullname] = score
            else:
                d[fullname] = max(d[fullname], score)

    res = [(k, v) for k, v in sorted(d.items(), key=lambda x: -x[1])]
    
    return res

def check_child_father_relation(affiliated_fio:str, 
                                names:NameModel, 
                                threshold:int = 70):
    fio_db = names.fio_db
    firstname_db = names.firstname_db
    
    text = affiliated_fio.split(' ')
    candidate_fathername = ' '.join(text[2:])
    
    # preprocess candidate_fathername
    if len(text) == 3:
        keyw = extract_name_from_fathersname(candidate_fathername)
    else:
        keyw = text[2]
    
    results = RapidFuzzChoices_Levenshtein(keyw, firstname_db, 40)    
   
    idscores = [(index, score) for _, score, index in results if score > threshold]
    results = [fio_db[id] for id, score in idscores]
    # results = [fio_db[id] for id, score in idscores if score > 80.0]
    
    possible_fos = generate_possible_father(affiliated_fio)
   
    d = {}
    for fio in possible_fos:
        curr = RapidFuzzChoices_Levenshtein(fio, results, 20)
        curr = [el for el in curr if el[1] >= threshold]
        for fullname, score, _ in curr:
            if fullname not in d:
                d[fullname] = score
            else:
                d[fullname] = max(d[fullname], score)
    
    res = [(k, v) for k, v in sorted(d.items(), key=lambda x: -x[1])]
    return res

def check_siblings_relation(affiliated_fio:str, names:NameModel):
    text = affiliated_fio.split(' ')
    family_name, father_name = text[0], text[2]
    
    same_secondnames = get_same_secondnames(family_name, names)
    result = []
    for i, same_secondname in enumerate(same_secondnames):
        x = same_secondname.split(' ')
        r = RapidFuzz_Levenshtein(father_name, x[2])
        if r > 70.0:
            result.append(same_secondnames[i])
        
    return result

def check_relavtive_relation(affiliated_fio:str, names:NameModel):
    text = affiliated_fio.split(' ')
    return get_same_secondnames(text[0], names)

def get_same_secondnames(keyw: str, 
                         names: NameModel, 
                         thresh: float = 84.0):
    fio_db = names.fio_db
    secondname_db = names.lastname_db
    
    result = RapidFuzzChoices_Levenshtein(keyw, secondname_db, 20)
    r = []
    for i in range(len(result)):
        secondname, score, idx = result[i]
        if score > thresh:
            r.append(result[i])
    
    res = [fio_db[idx] for _, _, idx in r]
    
    return res
  
def extract_name_from_fathersname(fathername: str) -> str:
     postfix = fathername[-4:]
     if postfix == 'ovna':
         return fathername[:-4]
     
     postfix = fathername[-5:]
     if postfix == "yevna":
         return fathername[:-5]
     elif postfix == 'ovich' or postfix == 'evich':
         return fathername[:-5]
     else:
         return fathername

def extract_name_from_familyname(familyname: str) -> str:
    if familyname[-1] == 'a': # sadulla yeva, prim ova, Axror ova, Ergash eva, Mirziya yeva, otajon ova,  
        if familyname[-3:] == 'ova':
            return familyname[:-3] 
        elif familyname[-4:] == 'yeva':
            return familyname[:-4]
    else:
        # Sadullayev, Ergashev, Boboqulov, Turdiboyev
        if familyname[-3:] == 'yev':
            return familyname[:-3]
        elif familyname[-2:] == 'ov':
            return familyname[:-2]

def generate_possible_father(person: str) -> list[str]:
    result = []
    text = person.split(' ')
    if len(text) == 3:
        candidate_fathername = ' '.join(text[2:])
        name = extract_name_from_fathersname(candidate_fathername)
    else:
        name = text[2]
    
    familyname = text[0]
    # result.append(familyname + ' ' + name)
    
    f_name = extract_name_from_familyname(text[0])
    if familyname[-1] == 'a':
        result.append(''.join(familyname[:-1]) + ' ' + name)
        # result.append(name + ' ' + f_name+'evna')
        # result.append(name + ' ' + f_name+'yevna')
        # result.append(name + ' ' + f_name+'ovna')
        # result.append(name + ' ' + f_name+" qizi")    
        # result.append(name + ' ' + f_name+" kizi") 
    else:
        result.append(familyname + ' ' + name)     
    result.append(name + ' ' + f_name+'ovich')
    result.append(name + ' ' + f_name+" o'g'li") 
    result.append(name + ' ' + f_name+" ugli") 
    result.append(name + ' ' + f_name+" ogli") 
    result.append(name + ' ' + f_name+" o'gli") 
    result.append(name + ' ' + f_name+" og'li") 
    
    return result

def generate_possible_child(person: str) -> list[str]:
    result = []
    text = person.split(' ')
    
    f_name = text[2]
    if len(text) == 3:
        f_name = extract_name_from_fathersname(f_name)
    
    result.append(f_name + 'ov ' + text[1] + 'vich')
    result.append(f_name + 'ov ' + text[1] + " o'g'li")
    result.append(text[0] + ' ' + text[1] + 'vich')
    result.append(text[0] + ' ' + text[1] + " o'g'li")
    
    return result
    