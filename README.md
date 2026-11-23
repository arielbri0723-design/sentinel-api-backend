# Sentinel API

Backend API desarrollada con FastAPI, PostgreSQL, Redis y Docker.

Infraestructura backend moderna preparada para aplicaciones escalables, con arquitectura modular, persistencia de datos, caché, monitorización mediante health checks, pruebas automatizadas y despliegue mediante contenedores.

---

## 🚀 Tecnologías

- Python 3.12
- FastAPI
- PostgreSQL + PostGIS
- Redis
- Docker
- Docker Compose
- Pytest
- HTTPX
- Pydantic Settings

---

## 📁 Arquitectura

```text
sentinel-api/
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

---

## ✨ Características

- API modular basada en FastAPI.
- PostgreSQL con almacenamiento persistente y soporte PostGIS.
- Redis protegido mediante autenticación y persistencia AOF.
- Health Checks para monitorización de servicios críticos.
- Variables de entorno centralizadas.
- Ejecución de contenedores mediante usuario sin privilegios.
- Pruebas automatizadas con Pytest y HTTPX.
- Orquestación de servicios mediante Docker Compose.

---

## ⚙️ Configuración

Crear el archivo de entorno:

### Linux / macOS

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

Completar las variables requeridas dentro de `.env`.

---

## ▶️ Ejecución local

```bash
docker compose up --build
```

La API quedará disponible en:

```text
http://localhost:8000
```

---

## 🔌 Servicios

| Servicio | Puerto |
|-----------|---------|
| API | 8000 |
| PostgreSQL | 5432 |
| PgAdmin (perfil `tools`) | 5050 |

---

## 📚 Documentación API

Una vez iniciada la aplicación:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## ❤️ Health Check

Verifica que la API se encuentra en ejecución.

```http
GET /health
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

---

## ✅ Readiness Check

Verifica la disponibilidad de PostgreSQL, PostGIS y Redis.

```http
GET /ready
```

Respuesta esperada cuando todos los servicios están operativos:

```json
{
  "status": "ok",
  "checks": {
    "database": true,
    "postgis": true,
    "redis": true
  }
}
```

Si alguna dependencia falla:

```http
HTTP/1.1 503 Service Unavailable
```

```json
{
  "status": "degraded",
  "checks": {
    "database": false,
    "postgis": true,
    "redis": true
  }
}
```

---

## 🧪 Pruebas

Ejecutar las pruebas automatizadas:

```bash
docker compose run --rm api pytest -q
```

---

## 🔒 Seguridad

- Usuario no root dentro del contenedor.
- Redis protegido mediante autenticación.
- Variables sensibles gestionadas mediante `.env`.
- Servicios expuestos únicamente en localhost durante el desarrollo.

---

## 📖 Acerca del proyecto

Sentinel API proporciona una base sólida para el desarrollo de aplicaciones backend modernas, incorporando persistencia de datos, caché, monitorización, pruebas automatizadas y despliegue mediante contenedores.

La arquitectura está preparada para evolucionar con nuevas funcionalidades y servicios de negocio manteniendo una estructura modular y escalable.

---

## 👨‍💻 Autor

**Ariel**

Desarrollador backend en formación enfocado en:

- Python
- FastAPI
- PostgreSQL
- Redis
- Docker
- APIs REST

GitHub: https://github.com/arielbri0723@gmail.com