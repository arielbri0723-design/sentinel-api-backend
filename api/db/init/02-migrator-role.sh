#!/bin/sh
# Crea el rol de migraciones (DDL) y la base descartable de tests.
# Con un volumen nuevo se ejecuta solo. En un volumen existente, una vez:
#   docker compose exec -T postgres sh /docker-entrypoint-initdb.d/02-migrator-role.sh
set -eu

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -v db_name="$POSTGRES_DB" -v migrator_password="$MIGRATION_PASSWORD" <<'SQL'
SELECT format(
  'CREATE ROLE sentinel_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L',
  :'migrator_password'
)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sentinel_migrator')\gexec
GRANT CONNECT ON DATABASE :"db_name" TO sentinel_migrator;
GRANT USAGE, CREATE ON SCHEMA public TO sentinel_migrator;
SQL

# CREATE DATABASE no puede ir dentro de una transacción: se genera y se ejecuta
# con \gexec, que además lo vuelve idempotente.
psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
SELECT 'CREATE DATABASE sentinel_test OWNER sentinel_migrator'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'sentinel_test')\gexec
SQL

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" --dbname "sentinel_test" <<'SQL'
CREATE EXTENSION IF NOT EXISTS postgis;
GRANT CONNECT ON DATABASE sentinel_test TO sentinel_app;
GRANT USAGE ON SCHEMA public TO sentinel_app;
SQL
