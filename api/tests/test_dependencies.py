"""Tests contra dependencias reales: Postgres con PostGIS y Redis.

Están marcados como `integration` y quedan fuera de la corrida por defecto
(ver pytest.ini). Necesitan la infraestructura de docker compose levantada.
"""

import uuid

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import make_conninfo

from app import db
from app.cache import check_redis
from app.config import Settings, get_settings

pytestmark = pytest.mark.integration


def test_database_responde():
    assert db.check_database() is True


def test_postgis_esta_instalado():
    assert db.check_postgis() is True


def test_redis_responde():
    assert check_redis() is True


def test_postgis_ausente_devuelve_false(monkeypatch):
    """El test que protege el fix de /ready.

    En una base SIN PostGIS, la implementación vieja
    (pg_available_extensions) devolvía True porque el binario está en el
    disco. Si alguien vuelve a esa consulta, este test falla.

    Crea una base temporal, apunta la configuración ahí y la borra al final.
    """
    settings = get_settings()
    nombre = f"test_sin_postgis_{uuid.uuid4().hex[:8]}"
    creada = False
    try:
        with psycopg.connect(settings.database_url, autocommit=True) as admin:
            admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(nombre)))
        creada = True

        url = make_conninfo(settings.database_url, dbname=nombre)
        monkeypatch.setattr(
            db,
            "get_settings",
            lambda: Settings(database_url=url, redis_url=settings.redis_url),
        )

        assert db.check_database() is True  # la base vacía sí responde
        assert db.check_postgis() is False  # pero no tiene PostGIS
    finally:
        if creada:
            with psycopg.connect(settings.database_url, autocommit=True) as admin:
                admin.execute(
                    sql.SQL("DROP DATABASE {} WITH (FORCE)").format(
                        sql.Identifier(nombre)
                    )
                )
