# Sentinel API

[![tests](https://github.com/arielbri0723-design/sentinel-api-backend/actions/workflows/tests.yml/badge.svg)](https://github.com/arielbri0723-design/sentinel-api-backend/actions/workflows/tests.yml)

Backend de una red de alerta para conductores, en desarrollo.
Este primer hito deja lista la base técnica: API, base de datos geoespacial, caché y pruebas automáticas.
Todavía no incluye las funciones de alertas ni la app móvil.

## Estado del proyecto

- **Hito 0 (completado):** infraestructura con Docker Compose, API en FastAPI con endpoints de salud y pruebas automáticas.
- **Hito 1 (en curso):** usuarios, autenticación, alertas y consulta de alertas cercanas con PostGIS.
  - **Fase 1 (completada):** capa de datos con SQLAlchemy 2.0 y Alembic, tabla `users`, roles separados para la API y las migraciones.
  - **Próximo:** registro, login y sesiones (Fase 2).

## Tecnologías

- Python 3.12 · FastAPI 0.115 · Pydantic Settings 2.7
- SQLAlchemy 2.0 · Alembic 1.20 · psycopg 3.2
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
│   │   ├── models/
│   │   │   ├── base.py         # DeclarativeBase de SQLAlchemy
│   │   │   └── user.py         # modelo User
│   │   ├── routers/
│   │   │   └── health.py
│   │   ├── cache.py           # cliente Redis y chequeo de salud
│   │   ├── config.py          # configuración desde el entorno
│   │   ├── database.py        # engine, sesiones y conexión a Postgres
│   │   ├── db.py              # chequeos de /ready
│   │   ├── main.py
│   │   └── ratelimit.py       # límite de peticiones por IP
│   ├── db/
│   │   └── init/
│   │       ├── 01-app-role.sh      # crea el rol sin privilegios
│   │       └── 02-migrator-role.sh # crea el rol DDL y la base de tests
│   ├── migrations/
│   │   ├── versions/
│   │   │   └── 0001_usuarios.py    # crea la tabla users
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_database.py       # engine y normalización de URL
│   │   ├── test_dependencies.py   # integración con Postgres y Redis reales
│   │   ├── test_health.py
│   │   ├── test_migrations.py     # upgrade/downgrade en sentinel_test
│   │   ├── test_permisos_db.py    # la API no puede hacer DDL
│   │   ├── test_ratelimit.py
│   │   └── test_user_model.py
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── alembic.ini
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
2. Abre `.env` y reemplaza los valores de ejemplo por contraseñas propias, largas, distintas entre sí y solo con letras y números. Los símbolos (`@ : / # ?`) rompen las URLs de conexión. Hay cinco contraseñas: `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `PGADMIN_PASSWORD`, `APP_PASSWORD` (la que usa la API para conectarse a Postgres) y `MIGRATION_PASSWORD` (solo la usan las migraciones). Este archivo no se sube al repositorio.
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

## Migraciones

El esquema lo administra Alembic. Las migraciones corren con el rol `sentinel_migrator`, que es el único con permisos DDL; la API usa `sentinel_app` y no puede crear ni borrar tablas. El servicio `migrate` no se levanta con `docker compose up`: se ejecuta a pedido.

```bash
# Aplicar las migraciones pendientes
docker compose --profile migrate run --rm migrate alembic upgrade head

# Ver la revisión actual
docker compose --profile migrate run --rm migrate alembic current

# Comprobar que los modelos y las migraciones estén sincronizados
docker compose --profile migrate run --rm migrate alembic check
```

Para probar la subida y la bajada completas se usa `migrate-test`, que apunta a la base descartable `sentinel_test` y nunca toca los datos reales:

```bash
docker compose --profile migrate run --rm migrate-test alembic downgrade base
docker compose --profile migrate run --rm migrate-test alembic upgrade head
```

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

Los tests de integración (marcados `integration`) sí hablan con Postgres y Redis reales, y requieren los servicios arriba. Se ejecutan en el servicio `migrate`, que es el único que tiene la URL con permisos DDL para probar las migraciones:

```bash
docker compose up -d
docker compose --profile migrate run --rm migrate python -m pytest -q -m integration
```

El comando `docker compose run --rm api python -m pytest -m integration` **no** sirve: la API no recibe `MIGRATION_DATABASE_URL` a propósito.

Uno de los tests fuerza `search_path=pg_catalog` para que `postgis_version()` no se resuelva y verifica que `check_postgis()` devuelva `false`. Es el test que impide que se repita el falso verde de `/ready`: con la implementación vieja (`pg_available_extensions`) falla.

En cada push a `main` y en cada pull request, GitHub Actions corre tres jobs en paralelo: los tests unitarios con Python 3.12, los tests dentro de la imagen Docker construida, y los de integración contra servicios reales de PostGIS y Redis. El job de integración crea los roles, la base `sentinel_test` y aplica las migraciones antes de correr los tests. También valida el `docker-compose.yml`. El estado se ve en el badge de arriba.

## Seguridad (nivel desarrollo)

- La API se conecta a Postgres con el rol `sentinel_app`, sin `SUPERUSER` ni `CREATEDB`. Es necesario para que las políticas RLS del Hito 1 se apliquen de verdad.
- Las migraciones usan un rol aparte, `sentinel_migrator`, con `CREATE` solo en el esquema `public`. La API nunca recibe esa clave.
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
