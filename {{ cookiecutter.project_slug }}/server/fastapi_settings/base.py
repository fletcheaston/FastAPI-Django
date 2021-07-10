from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    DEBUG: bool = False
    CORS_ORIGINS: List[str]

    COOKIE_NAME: str = "cookies-please"

    # Database settings
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_HOST: str
    DATABASE_PORT: str = ""
    DATABASE_URI: Optional[str] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_database_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        user = values.get("DATABASE_USER")
        password = values.get("DATABASE_PASSWORD")
        name = values.get("DATABASE_NAME")
        host = values.get("DATABASE_HOST")
        url = f"postgresql+psycopg2://{user}:{password}@/{name}?host={host}"
        return url
