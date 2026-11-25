#!/bin/sh
# Se ejecuta una sola vez, cuando el volumen de Postgres está vacío.
# La API no usa el superusuario del cluster: RLS no se aplicaría a él.
set -eu

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -v db_name="$POSTGRES_DB" -v app_password="$APP_PASSWORD" <<'SQL'
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sentinel_app') THEN
    CREATE ROLE sentinel_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
      PASSWORD :'app_password';
  END IF;
END
$$;
GRANT CONNECT ON DATABASE :"db_name" TO sentinel_app;
GRANT USAGE ON SCHEMA public TO sentinel_app;
SQL
