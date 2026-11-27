"""El rol de la API no puede hacer DDL y las tablas son del rol migrador."""

import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from app.database import engine

pytestmark = pytest.mark.integration

API_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module", autouse=True)
def _migraciones_aplicadas() -> None:
    url = os.environ.get("MIGRATION_DATABASE_URL")
    if not url:
        pytest.fail(
            "Falta MIGRATION_DATABASE_URL. Los tests de permisos se corren "
            "en el servicio migrate."
        )
    config = Config(str(API_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(API_DIR / "migrations"))
    command.upgrade(config, "head")


def test_la_api_no_puede_crear_tablas() -> None:
    with engine.connect() as connection:
        with pytest.raises(ProgrammingError):
            connection.execute(text("CREATE TABLE public.debe_fallar (id int)"))
        connection.rollback()


def test_las_tablas_pertenecen_al_rol_de_migraciones() -> None:
    with engine.connect() as connection:
        propietario = connection.execute(
            text(
                "SELECT tableowner FROM pg_tables "
                "WHERE schemaname = 'public' AND tablename = 'users'"
            )
        ).scalar_one()
    assert propietario == "sentinel_migrator"
