from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Vienen del entorno (docker-compose las inyecta desde el archivo .env).
    database_url: str
    redis_url: str


@lru_cache
def get_settings() -> Settings:
    """Se parsea el entorno una sola vez por proceso."""
    return Settings()
