"""Las migraciones suben y bajan en una base descartable, nunca en la real."""

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from app.database import _normalizar_url

pytestmark = pytest.mark.integration

API_DIR = Path(__file__).resolve().parents[1]


def _config() -> Config:
    config = Config(str(API_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(API_DIR / "migrations"))
    return config


@pytest.fixture()
def configurar_base_de_test(monkeypatch: pytest.MonkeyPatch) -> None:
    """Apunta Alembic a la base descartable.

    No devuelve la URL: si un test falla, pytest imprimiría el valor del
    fixture y con él la clave. El test la lee del entorno cuando la necesita.
    """
    url = os.environ.get("TEST_MIGRATION_DATABASE_URL")
    if not url:
        pytest.fail(
            "Falta TEST_MIGRATION_DATABASE_URL. Los tests de migraciones "
            "se corren en el servicio migrate."
        )
    monkeypatch.setenv("MIGRATION_DATABASE_URL", url)


@pytest.fixture()
def test_engine(
    configurar_base_de_test: None,
) -> Generator[Engine, None, None]:
    url = os.environ["TEST_MIGRATION_DATABASE_URL"]
    engine = create_engine(_normalizar_url(url))
    yield engine
    engine.dispose()


def test_las_migraciones_suben_y_bajan(test_engine: Engine) -> None:
    config = _config()

    if inspect(test_engine).has_table("alembic_version"):
        command.downgrade(config, "base")

    command.upgrade(config, "head")

    inspector = inspect(test_engine)
    assert inspector.has_table("users")
    columnas = {columna["name"] for columna in inspector.get_columns("users")}
    assert columnas == {"id", "email", "password_hash", "created_at", "is_active"}
    unicas = inspector.get_unique_constraints("users")
    assert any(item["column_names"] == ["email"] for item in unicas)
    checks = inspector.get_check_constraints("users")
    assert any("lower" in item["sqltext"] for item in checks)

    with test_engine.connect() as connection:
        propietario = connection.execute(
            text(
                "SELECT tableowner FROM pg_tables "
                "WHERE schemaname = 'public' AND tablename = 'users'"
            )
        ).scalar_one()
    assert propietario == "sentinel_migrator"

    with test_engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (email, password_hash) "
                "VALUES (:email, :password_hash)"
            ),
            {"email": "persona@ejemplo.com", "password_hash": "hash-de-prueba"},
        )

    with pytest.raises(IntegrityError):
        with test_engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO users (email, password_hash) "
                    "VALUES (:email, :password_hash)"
                ),
                {"email": "persona@ejemplo.com", "password_hash": "otro-hash"},
            )

    with pytest.raises(IntegrityError):
        with test_engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO users (email, password_hash) "
                    "VALUES ('MAYUSCULAS@EJEMPLO.COM', 'hash-de-prueba')"
                )
            )

    command.downgrade(config, "base")
    assert not inspect(test_engine).has_table("users")

    command.upgrade(config, "head")
