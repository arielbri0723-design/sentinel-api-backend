# Sentinel API — contexto del proyecto

Backend de una red de alertas para conductores. Proyecto personal de aprendizaje:
está en desarrollo y todavía no incluye las funciones de alertas ni la app móvil.

## Stack

- Python 3.12, FastAPI, Uvicorn, Pydantic Settings
- PostgreSQL 16 + PostGIS 3.4 (`postgis/postgis:16-3.4`)
- Redis 7 con contraseña y persistencia AOF
- Docker Compose, pytest, HTTPX

## Estado

- Hito 0 (completado): infraestructura, API con `/health` y `/ready`, tests y CI.
- Próximo, Hito 1: usuarios, crear alertas y consultar alertas cercanas con PostGIS.

## Comandos

```bash
# levantar todo
docker compose up --build

# tests unitarios (no necesitan infraestructura)
docker compose run --rm --no-deps api python -m pytest -q

# tests de integración (requieren Postgres y Redis arriba)
docker compose up -d
docker compose run --rm api python -m pytest -q -m integration

# estado y logs
docker compose ps
docker compose logs -f api
```

## Convenciones

- Commits y documentación en español; mensajes con conventional commits
  (`feat:`, `fix:`, `docs:`, `ci:`, `test:`, `chore:`).
- Mantener las dependencias pinneadas en `api/requirements.txt`.
- Los tests de integración llevan el marker `integration` y no corren por defecto.
- `/docs`, `/redoc` y `/openapi.json` están desactivados a propósito.

## Entorno y datos (importante)

- El repo y `.env.example` usan `POSTGRES_DB=sentinel` y `POSTGRES_USER=sentinel`.
- El `.env` local de esta máquina todavía usa `redalerta`, a propósito, porque el
  volumen `sentinel-api-backend_pgdata` ya existe con ese nombre. Cambiarlo sin
  migrar la base rompe la conexión de la API.
- No ejecutar `docker compose down -v` salvo que se quiera borrar los datos.
- Para migrar el entorno local: renombrar base y rol dentro de Postgres y actualizar
  `.env`, o recrear el volumen si no importan los datos.

## CI

`.github/workflows/tests.yml` corre en cada push a `main`: pytest con Python 3.12,
tests dentro de la imagen Docker e integración con servicios reales de PostGIS y
Redis.
