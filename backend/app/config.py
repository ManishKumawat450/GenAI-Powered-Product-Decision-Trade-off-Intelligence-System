from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://decision_user:decision_pass@localhost:5432/decision_db"
    JWT_SECRET: str = "change_me_to_random_32char_secret_here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    LLM_PROVIDER: str = ""
    LLM_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
