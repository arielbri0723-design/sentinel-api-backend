"""Tests contra dependencias reales: Postgres con PostGIS y Redis.

Están marcados como `integration` y quedan fuera de la corrida por defecto
(ver pytest.ini). Necesitan la infraestructura de docker compose levantada.
"""

import pytest

from app import db
from app.cache import check_redis

pytestmark = pytest.mark.integration


def test_database_responde():
    assert db.check_database() is True


def test_postgis_esta_instalado():
    assert db.check_postgis() is True


def test_redis_responde():
    assert check_redis() is True


def test_la_api_no_usa_superusuario():
    """RLS no se aplica a superusuarios: este test impide volver a usar uno."""
    with db._connect() as conn:
        es_superusuario, puede_crear_bases = conn.execute(
            "SELECT rolsuper, rolcreatedb FROM pg_roles WHERE rolname = current_user"
        ).fetchone()
    assert es_superusuario is False
    assert puede_crear_bases is False


def test_postgis_ausente_devuelve_false(monkeypatch):
    """El test que protege el fix de /ready.

    Con search_path=pg_catalog, postgis_version() no se resuelve: reproduce
    exactamente el fallo de una base sin la extensión, sin crear bases
    temporales (la API ya no tiene permiso CREATEDB). Con la implementación
    vieja (pg_available_extensions) este test falla, porque esa tabla vive en
    pg_catalog y sigue respondiendo que PostGIS está disponible.
    """
    conectar = db._connect

    def conectar_sin_postgis():
        conn = conectar()
        conn.execute("SET search_path = pg_catalog")
        return conn

    monkeypatch.setattr(db, "_connect", conectar_sin_postgis)

    assert db.check_postgis() is False
