from fastapi import FastAPI

from .routers import health

# Sin documentación pública: se activará solo en desarrollo.
app = FastAPI(
    title="Sentinel API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(health.router)
