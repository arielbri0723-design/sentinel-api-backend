import psycopg

from .config import get_settings


def check_database() -> bool:
    """Comprueba que Postgres responde."""
    try:
        with psycopg.connect(get_settings().database_url, connect_timeout=3) as conn:
            return conn.execute("SELECT 1").fetchone() == (1,)
    except Exception:
        return False


def check_postgis() -> bool:
    """Comprueba que la extensión PostGIS está disponible (solo lectura)."""
    try:
        with psycopg.connect(get_settings().database_url, connect_timeout=3) as conn:
            row = conn.execute(
                "SELECT 1 FROM pg_available_extensions WHERE name = 'postgis'"
            ).fetchone()
            return row is not None
    except Exception:
        return False
