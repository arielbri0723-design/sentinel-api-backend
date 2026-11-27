"""Capa única de acceso a datos: SQLAlchemy 2.0 síncrono.

La API se conecta con el rol `sentinel_app`, que no tiene permisos DDL.
Las migraciones usan otro rol y viven en `migrations/`, nunca en este módulo.
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings


def _normalizar_url(url: str) -> str:
    """SQLAlchemy necesita nombrar el dialecto para usar psycopg 3.

    El `.env` sigue usando el formato estándar `postgresql://`; acá se
    traduce a `postgresql+psycopg://` sin tocar la configuración.
    """
    for prefijo in ("postgresql://", "postgres://"):
        if url.startswith(prefijo):
            return "postgresql+psycopg://" + url[len(prefijo) :]
    return url


engine: Engine = create_engine(
    _normalizar_url(get_settings().database_url),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "connect_timeout": 3,
        # Sin esto, una consulta colgada deja /ready esperando para siempre.
        "options": "-c statement_timeout=3000",
    },
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_session() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: una sesión por petición."""
    with SessionLocal() as session:
        yield session


@contextmanager
def probe_connection() -> Generator[Connection, None, None]:
    """Conexión corta para los chequeos de /ready."""
    with engine.connect() as connection:
        yield connection
