from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os, shutil
from datetime import date

from sqlalchemy import select, text

from src.models import DocumentsOrm, DocumentsTextOrm
from src.db import session_factory, engine

from tasks import process_doc

app = FastAPI()

@app.post(
    "/upload_files/",
    summary="Загрузка картинок",
    description="Загружает один или несколько картинок на сервер и сохраняет путь и дату в базу данных.",
    response_description="Успешная загрузка картинок"
)
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

    return {"message": f"{len(files)} картин(ок) успешно загружено."}

@app.delete(
    "/delete_files/{id_doc}",
    summary="Удаление картинок",
    description="Удаляет картинку с сервера и запись о нёй из базы данных по id_doc.",
    responses={
        200: {"description": "Файл успешно удалён"},
        404: {"description": "Документ не найден"}
    }
)
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
    return {"message": f"Документ с ID {id_doc} успешно удалён."}


@app.post(
    '/doc_analyse/{id_doc}',
    summary="Поставить картинку в очередь на обработку",
    description="Отправляет задачу по анализу картинки по id_doc в очередь Celery.",
    responses={
        200: {"description": "Документ поставлен в очередь"}
    }
)
def doc_analyse(id_doc: int):
    process_doc.apply_async([id_doc])
    return {"message": f"Картинка {id_doc} поставлена в очередь на обработку."}


@app.get(
    '/get_text/{id_doc}',
    summary="Получение текста картинки",
    description="Возвращает ранее извлечённый текст из картинки по его id_doc из DocumentsTextOrm.",
    responses={
        200: {"description": "Текст успешно получен"},
        404: {"description": "Документ с текстом не найден"}
    }
)
def get_text(id_doc: int):
    with session_factory() as session:
        query = select(DocumentsTextOrm).where(DocumentsTextOrm.id_doc == id_doc)
        result = session.execute(query)
        text_msg = result.scalar_one_or_none()

        if not text_msg:
            raise HTTPException(status_code=404, detail="Текст документа не найден")

        return {'test':text_msg.text}