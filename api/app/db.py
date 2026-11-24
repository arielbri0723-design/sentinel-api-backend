import logging

import psycopg

from .config import get_settings

logger = logging.getLogger(__name__)

# connect_timeout solo cubre el saludo inicial: si la consulta se cuelga
# después, /ready quedaría esperando para siempre.
_OPTIONS = "-c statement_timeout=3000"


def _connect():
    return psycopg.connect(
        get_settings().database_url,
        connect_timeout=3,
        options=_OPTIONS,
    )


def check_database() -> bool:
    """Comprueba que Postgres responde."""
    try:
        with _connect() as conn:
            return conn.execute("SELECT 1").fetchone() == (1,)
    except Exception:
        # El cliente ve solo un booleano; el detalle queda en el log del servidor.
        logger.warning("Postgres no responde", exc_info=True)
        return False


def check_postgis() -> bool:
    """Comprueba que PostGIS está INSTALADO y usable, no solo disponible.

    pg_available_extensions responde "puedo instalarlo", y en la imagen
    postgis/postgis eso es siempre verdad aunque falte el CREATE EXTENSION.
    postgis_version() obliga a cargar la extensión: si no está, falla.
    """
    try:
        with _connect() as conn:
            return conn.execute("SELECT postgis_version()").fetchone() is not None
    except Exception:
        logger.warning("PostGIS no está instalado o no responde", exc_info=True)
        return False
