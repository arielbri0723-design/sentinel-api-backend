"""Entorno de Alembic.

La URL de migraciones viene SIEMPRE de `MIGRATION_DATABASE_URL`, que usa un
rol con DDL. La API en runtime nunca recibe esa variable.
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Tablas que instala PostGIS y que no pertenecen a la aplicación. Sin esto,
# `alembic check`/autogenerate las interpreta como tablas borradas.
_TABLAS_DE_POSTGIS = {"spatial_ref_sys", "layer", "topology"}


def _incluir_objeto(_objeto, nombre, tipo, _reflejado, _comparado) -> bool:
    return not (tipo == "table" and nombre in _TABLAS_DE_POSTGIS)


def _normalizar_url(url: str) -> str:
    for prefijo in ("postgresql://", "postgres://"):
        if url.startswith(prefijo):
            return "postgresql+psycopg://" + url[len(prefijo) :]
    return url


def _database_url() -> str:
    url = os.environ.get("MIGRATION_DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Falta MIGRATION_DATABASE_URL: las migraciones necesitan un rol "
            "con permisos DDL."
        )
    return _normalizar_url(url)


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=_incluir_objeto,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuracion = config.get_section(config.config_ini_section, {})
    configuracion["sqlalchemy.url"] = _database_url()
    connectable = engine_from_config(
        configuracion,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_object=_incluir_objeto,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
