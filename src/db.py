from src.config import settings

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine(
    url = settings.get_database_url
)

session_factory = sessionmaker(engine)

class Base(DeclarativeBase):
    ...