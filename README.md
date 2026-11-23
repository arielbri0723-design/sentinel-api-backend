Backend API desarrollada con FastAPI, PostgreSQL, Redis y Docker.

Infraestructura backend preparada para aplicaciones escalables, con arquitectura modular, persistencia de datos, caché distribuida y despliegue mediante contenedores.

## Tecnologías

- Python 3.12
- FastAPI
- PostgreSQL + PostGIS
- Redis
- Docker
- Docker Compose
- Pytest
- HTTPX
- Pydantic Settings

## Arquitectura

```text
alerta-roja/
│
├── api/
│   ├── app/
│   │   ├── routers/
│   │   ├── cache.py
│   │   ├── config.py
│   │   ├── db.py
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## Características

- API modular basada en FastAPI.
- PostgreSQL con almacenamiento persistente.
- Redis protegido mediante contraseña.
- Health checks para servicios críticos.
- Variables de entorno centralizadas.
- Ejecución de contenedores mediante usuario sin privilegios.
- Soporte para pruebas automatizadas.
- Orquestación de servicios mediante Docker Compose.

## Configuración

Crear el archivo de entorno:

```bash
cp .env.example .env
```

Completar las variables requeridas dentro de `.env`.

## Ejecución local

```bash
docker compose up --build
```

## Servicios

| Servicio | Puerto |
|-----------|---------|
| API | 8000 |
| PostgreSQL | 5432 |
| PgAdmin (opcional) | 5050 |

## Verificación

Endpoint de salud:

```http
GET /health
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

## Pruebas

Ejecutar las pruebas automatizadas:

```bash
docker compose run --rm api pytest -q
```

## Seguridad

- Usuario no root dentro del contenedor.
- Redis protegido mediante contraseña.
- Configuración sensible gestionada mediante variables de entorno.
- Servicios expuestos únicamente en localhost durante el desarrollo.




