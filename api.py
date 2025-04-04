from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os, shutil
from datetime import date

from sqlalchemy import select

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

@app.delete("/delete_files/{id_doc}")
def delete_file(id_doc: int):
    with session_factory() as session:
        query = select(DocumentsOrm).where(DocumentsOrm.id == id_doc)
        result = session.execute(query)
        provider = result.scalar_one_or_none()

        if not provider:
            raise HTTPException(status_code=404, detail="Document not found")

        if os.path.exists(provider.path):
            os.remove(provider.path)

        session.delete(provider)
        session.commit()