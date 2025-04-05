from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os, shutil
from datetime import date

from sqlalchemy import select, text

from src.models import DocumentsOrm, DocumentsTextOrm
from src.db import session_factory, engine

from tasks import process_doc

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
        doc = result.scalar_one_or_none()

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if os.path.exists(doc.path):
            os.remove(doc.path)

        session.delete(doc)
        session.commit()

@app.post('/doc_analyse/{id_doc}')
def doc_analyse(id_doc: int):
    process_doc.apply_async([id_doc])
    return {"message": f"Документ {id_doc} поставлен в очередь на обработку."}
