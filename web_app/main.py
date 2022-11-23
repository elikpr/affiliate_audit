import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from models import DBModel
from affilate_check import check_all
from utils import save_file_to_server, load_db, list_to_model

app = FastAPI()
dbs = {} # "str" : "NameModel"
    
@app.post("/api/upload_xls_db")
def upload_xms_db(db_name: str, db_xml_file: UploadFile = File(...)):
    response = {}
    saved_path = save_file_to_server(db_xml_file, save_as=db_name)
    db = load_db(xls_filename=saved_path, is_list=True)
    dbs[db_name] = db
    response["uploaded"] = db_name
    return response

# @app.post("/api/upload_list_db")
# def upload_list_db(db_name: str, db: DBModel):
#     raise NotImplementedError

@app.get("/api/check_vs_regdb")
def check_vs_regdb(db_name: str, affiliate_name: str):
    curr_db = dbs.get(db_name, None)
    if curr_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"[{db_name}] db is not registered"
        )
    result = check_all(affiliate_name, curr_db)
    return result

@app.post("/api/check_vs_injdb")
async def check_vs_injdb(affiliate_name: str, fio_db: DBModel):
    db = list_to_model(fio_db.fullnames, True)
    result = check_all(affiliate_name, db)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)