from typing import List

from .base import Settings as BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:4200",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:4200",
    ]

    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""
    DATABASE_HOST: str = "localhost"
    DATABASE_NAME: str = "postgres"
