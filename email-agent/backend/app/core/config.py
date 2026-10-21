import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str
    database_url: str


@lru_cache
def get_settings() -> Settings:
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db = os.getenv("POSTGRES_DB", "email_agent")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")

    database_url = os.getenv("DATABASE_URL") or (
        f"postgresql://{user}:{password}@{host}:{port}/{db}"
    )
    # SQLAlchemy cần chỉ định driver psycopg (v3)
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return Settings(
        postgres_user=user,
        postgres_password=password,
        postgres_db=db,
        postgres_host=host,
        postgres_port=port,
        database_url=database_url,
    )
