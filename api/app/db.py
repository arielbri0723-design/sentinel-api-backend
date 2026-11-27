import logging

from sqlalchemy import text
from sqlalchemy.engine import Connection

from .database import probe_connection

logger = logging.getLogger(__name__)


def _postgis_version(connection: Connection) -> bool:
    """Devuelve True solo si postgis_version() se puede ejecutar."""
    try:
        version = connection.execute(text("SELECT postgis_version()"))
        return version.scalar_one() is not None
    except Exception:
        logger.warning("PostGIS no está instalado o no responde", exc_info=True)
        return False


def check_database() -> bool:
    """Comprueba que Postgres responde."""
    try:
        with probe_connection() as connection:
            return connection.execute(text("SELECT 1")).scalar_one() == 1
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
        with probe_connection() as connection:
            return _postgis_version(connection)
    except Exception:
        logger.warning("PostGIS no está instalado o no responde", exc_info=True)
        return False
