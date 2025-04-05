from celery import Celery

from src.config import settings

from src.db import session_factory

from src.models import DocumentsOrm, DocumentsTextOrm

from sqlalchemy import select

from PIL import Image
import pytesseract


celery_app = Celery("tasks", brocker="settings.get_broker_url")

@celery_app.task
def process_doc(id_doc: int):
    ...
    with session_factory() as session:
        query = select(DocumentsOrm).where(DocumentsOrm.id == id_doc)
        result = session.execute(query)
        doc_path = (result.scalar_one_or_none()).path

        image = Image.open(doc_path)
        text = pytesseract.image_to_string(image)
        session.add(DocumentsTextOrm(
            id_doc = id_doc,
            text = text
        ))
        session.commit()