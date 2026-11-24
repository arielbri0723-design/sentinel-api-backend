# Sentinel API

Backend de una red de alerta para conductores, en desarrollo.
Este primer hito deja lista la base técnica: API, base de datos geoespacial, caché y pruebas automáticas.
Todavía no incluye las funciones de alertas ni la app móvil.

## Estado del proyecto

- **Hito 0 (completado):** infraestructura con Docker Compose, API en FastAPI con endpoints de salud y pruebas automáticas.
- **Próximo, Hito 1:** usuarios, crear alertas y consultar alertas cercanas con PostGIS.

## Tecnologías

Python 3.12 · FastAPI · PostgreSQL + PostGIS · Redis · Docker y Docker Compose · Pytest · HTTPX · Pydantic Settings

## Estructura

```text
sentinel-api-backend/
├── api/
│   ├── app/
│   │   ├── routers/
│   │   ├── cache.py
│   │   ├── config.py
│   │   ├── db.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Cómo ejecutarlo

Requisito: Docker Desktop.

1. Crea tu archivo de entorno:
   - Windows PowerShell: `Copy-Item .env.example .env`
   - Linux / macOS: `cp .env.example .env`
2. Abre `.env` y reemplaza los valores de ejemplo por contraseñas propias, largas, distintas entre sí y solo con letras y números. Este archivo no se sube al repositorio.
3. Levanta los servicios:

```bash
docker compose up --build
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

- `GET /health`: la API está viva. Responde `{"status": "ok"}`.
- `GET /ready`: revisa PostgreSQL, PostGIS y Redis. Responde 200 si todo está bien y 503 si alguna dependencia falla.

```json
{ "status": "ok", "checks": { "database": true, "postgis": true, "redis": true } }
```

La documentación automática (`/docs`) está desactivada a propósito.

## Pruebas

```bash
docker compose run --rm api python -m pytest -q
```

## Seguridad (nivel desarrollo)

- El contenedor de la API corre sin privilegios de administrador.
- Redis exige contraseña y guarda sus datos con persistencia AOF.
- Las contraseñas viven en `.env`, que está en `.gitignore`.
- Los servicios solo escuchan en localhost.

## Autor

**Ariel Britez**: maquinista industrial que se está formando en Python y desarrollo de software. Este es mi primer proyecto backend.

GitHub: https://github.com/arielbri0723-design
