# Sentinel API

[![tests](https://github.com/arielbri0723-design/sentinel-api-backend/actions/workflows/tests.yml/badge.svg)](https://github.com/arielbri0723-design/sentinel-api-backend/actions/workflows/tests.yml)

Backend de una red de alerta para conductores, en desarrollo.
Este primer hito deja lista la base técnica: API, base de datos geoespacial, caché y pruebas automáticas.
Todavía no incluye las funciones de alertas ni la app móvil.

## Estado del proyecto

- **Hito 0 (completado):** infraestructura con Docker Compose, API en FastAPI con endpoints de salud y pruebas automáticas.
- **Próximo, Hito 1:** usuarios, crear alertas y consultar alertas cercanas con PostGIS.

## Tecnologías

- Python 3.12 · FastAPI 0.115 · Pydantic Settings 2.7
- PostgreSQL 16 con PostGIS 3.4 (`postgis/postgis:16-3.4`)
- Redis 7 (persistencia AOF, con contraseña)
- Docker y Docker Compose
- Pytest 8.3 · HTTPX 0.28

## Estructura

```text
sentinel-api-backend/
├── .github/
│   ├── dependabot.yml         # actualizaciones semanales
│   └── workflows/
│       └── tests.yml          # CI: tests, imagen Docker e integración
├── api/
│   ├── app/
│   │   ├── routers/
│   │   │   └── health.py
│   │   ├── cache.py           # cliente Redis y chequeo de salud
│   │   ├── config.py          # configuración desde el entorno
│   │   ├── db.py              # conexión a Postgres y chequeos
│   │   ├── main.py
│   │   └── ratelimit.py       # límite de peticiones por IP
│   ├── db/
│   │   └── init/
│   │       └── 01-app-role.sh # crea el rol sin privilegios
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_dependencies.py   # integración con Postgres y Redis reales
│   │   ├── test_health.py
│   │   └── test_ratelimit.py
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── LICENSE
└── README.md
```

## Cómo ejecutarlo

Requisito: Docker Desktop **iniciado** (si no, `docker compose` falla con `cannot connect to the Docker daemon`).

1. Crea tu archivo de entorno:
   - Windows PowerShell: `Copy-Item .env.example .env`
   - Linux / macOS: `cp .env.example .env`
2. Abre `.env` y reemplaza los valores de ejemplo por contraseñas propias, largas, distintas entre sí y solo con letras y números. Los símbolos (`@ : / # ?`) rompen las URLs de conexión. Hay cuatro contraseñas: `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `PGADMIN_PASSWORD` y `APP_PASSWORD` (la que usa la API para conectarse a Postgres). Este archivo no se sube al repositorio.
3. Levanta los servicios:

```bash
docker compose up --build
```

## Comandos útiles

```bash
docker compose ps                    # estado y salud de cada contenedor
docker compose logs -f api           # ver los logs de la API en vivo
docker compose down                  # apagar (los datos se conservan)
```

> `docker compose down -v` borra también los volúmenes: **se pierden todos los datos** de Postgres y Redis. Solo para empezar de cero.

## Servicios y puertos

Todos se exponen solo en `127.0.0.1` (tu computadora).

| Servicio | Puerto |
|---|---|
| API | 8000 |
| PostgreSQL + PostGIS | 5432 |
| pgAdmin (opcional: `docker compose --profile tools up`) | 5050 |

Redis solo es accesible desde la red interna de Docker.

## Endpoints

- `GET /health`: la API está viva. No toca la base ni Redis.

```json
{ "status": "ok" }
```

- `GET /ready`: revisa PostgreSQL, PostGIS y Redis. Responde 200 si todo está bien y 503 si alguna dependencia falla. Los tres chequeos se ejecutan siempre, así se ve todo lo que está roto y no solo la primera falla.

```json
{ "status": "ok", "checks": { "database": true, "postgis": true, "redis": true } }
```

```json
{ "status": "degraded", "checks": { "database": true, "postgis": true, "redis": false } }
```

El chequeo de PostGIS no se conforma con que la extensión esté *disponible*: llama a `postgis_version()`, así que si falta el `CREATE EXTENSION` responde `false` en vez de dar un falso positivo.

La documentación automática (`/docs`, `/redoc`, `/openapi.json`) está desactivada a propósito.

## Pruebas

Los tests de la API simulan las dependencias, así que no necesitan Postgres ni Redis levantados:

```bash
docker compose run --rm --no-deps api python -m pytest -q
```

Los tests de integración (marcados `integration`) sí hablan con Postgres y Redis reales, y requieren los servicios arriba:

```bash
docker compose up -d
docker compose run --rm api python -m pytest -q -m integration
```

Uno de ellos crea una base temporal **sin** PostGIS y verifica que `check_postgis()` devuelva `false`. Es el test que impide que se repita el falso verde de `/ready`: con la implementación vieja (`pg_available_extensions`) falla.

En cada push a `main`, GitHub Actions corre tres jobs en paralelo: los tests unitarios con Python 3.12, los tests dentro de la imagen Docker construida, y los de integración contra servicios reales de PostGIS y Redis. También valida el `docker-compose.yml`. El estado se ve en el badge de arriba.

## Seguridad (nivel desarrollo)

- La API se conecta a Postgres con el rol `sentinel_app`, sin `SUPERUSER` ni `CREATEDB`. Es necesario para que las políticas RLS del Hito 1 se apliquen de verdad.
- `/ready` acepta hasta 30 peticiones por minuto por IP (429 y `Retry-After` después); el resto de las rutas, 120. Las respuestas llevan headers de seguridad y no exponen CORS.
- El contenedor de la API corre como usuario sin privilegios (`appuser`), no como root.
- Redis exige contraseña y guarda sus datos con persistencia AOF.
- Las contraseñas viven en `.env`, que está en `.gitignore`.
- Los servicios solo escuchan en localhost.
- El acceso a la base se limita con `connect_timeout` y `statement_timeout`, para que `/ready` nunca quede colgado.

## Sobre el desarrollo

Este proyecto es mi práctica para aprender backend. Lo construyo con ayuda de asistentes de IA para planificar, revisar y entender el código, y voy documentando lo que aprendo en cada hito.

## Autor

**Ariel Britez**: maquinista industrial que se está formando en Python y desarrollo de software. Este es mi primer proyecto backend.

GitHub: https://github.com/arielbri0723-design

## Licencia

MIT — ver [LICENSE](LICENSE).
