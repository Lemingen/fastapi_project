from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os, shutil
from datetime import date

from src.models import DocumentsOrm, DocumentsTextOrm
from src.db import session_factory, engine

app = FastAPI()

@app.post("/upload_files/")
def upload_file(files: list[UploadFile] = File(...)):
    UPLOAD_DIR = 'documents'
    doc_lst=[]
    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)  # Путь к файлу в папке
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        doc_lst.append( DocumentsOrm(
            path = file_location,
            date = date.today()
        ))
    with session_factory() as session:
        session.add_all(doc_lst)
        session.commit()

    #return {"message": f"File '{file.filename}' uploaded successfully!"}