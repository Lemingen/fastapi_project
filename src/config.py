from dotenv import load_dotenv

from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    CELERY_BROKER_URL: str

    @property
    def get_database_url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def get_broker_url(self):
        return self.CELERY_BROKER_URL

settings = Settings()