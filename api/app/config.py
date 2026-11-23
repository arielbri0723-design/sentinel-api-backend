from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Vienen del entorno (docker-compose las inyecta desde el archivo .env).
    database_url: str
    redis_url: str


def get_settings() -> Settings:
    return Settings()
