from pydantic import BaseModel


class DBModel(BaseModel):
    fullnames: list
    
class NameModel(BaseModel):
    fio_db: list
    firstname_db: list
    lastname_db: list
    fathername_db: list