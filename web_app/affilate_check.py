from models import DBModel, NameModel
# from web_app import utils
import utils


def check_all(affiliated_fio: str, fio_model: NameModel) -> dict:
    result = {}
    
    is_same_person, score = check_same_person(affiliated_fio, fio_model.fio_db)
    result["SamePerson"] = is_same_person
    result["FatherChild"] = None
    result["ChildFather"] = None
    result["Siblings"] = None
    result["Potential"] = None
    result["OtherRelations"] = None
    if score < 100:
        father_child = check_father_child(affiliated_fio, fio_model)
        father_child = father_child[:min(5, len(father_child))]
        result["FatherChild"] = father_child
        
        child_father = check_child_father(affiliated_fio, fio_model)
        result["ChildFather"] = child_father[:min(5, len(child_father))]
        
        siblings = check_siblings(affiliated_fio, fio_model)
        result["Siblings"] = siblings[:min(5, len(siblings))]
        
        potential = check_potential(affiliated_fio, fio_model)
        result["Potential"] = potential[:min(5, len(potential))]
        
        other_candidates = check_other(affiliated_fio, fio_model)
        result["OtherRelations"] = other_candidates[:min(5, len(other_candidates))]
    
    return result
    
def check_same_person(affiliated_fio: str, fio: list):
    """Checks if affiliated person works in the company"""
    result = utils.RapidFuzzChoices_Levenshtein(affiliated_fio, fio, 1)
    score = result[0][1]
    print("SamePerson:")
    print(f"Candidate: {affiliated_fio}, score: {score}")
    return 95<=score<=100, score

def check_father_child(affiliated_fio: str, fio_model: NameModel):
    result = utils.check_father_child_relation(affiliated_fio, fio_model)
    return result

def check_child_father(affiliated_fio: str, fio_model: NameModel):
    result = utils.check_child_father_relation(affiliated_fio, fio_model)
    return result

def check_siblings(affiliated_fio: str, fio_model: NameModel):
    result = utils.check_siblings_relation(affiliated_fio, fio_model)
    return result

def check_potential(affiliated_fio: str, fio_model: NameModel):
    result = utils.check_relavtive_relation(affiliated_fio, fio_model)
    return result

def check_other(affileated_fio: str, fio_model: NameModel):
    result = utils.RapidFuzzChoices_Levenshtein(affileated_fio, fio_model.fio_db, 10)
    return result