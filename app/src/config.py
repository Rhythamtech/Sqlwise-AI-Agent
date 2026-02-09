from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    OPENAI_MODEL: str
    DB_SERVER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DRIVER: str
    COHERE_API_KEY: str
    QDRANT_URL: str
    TOKENIZERS_PARALLELISM : bool
   # VECTOR_DB_PATH: str

    class Config:
        env_file = ".env"

settings = Settings()