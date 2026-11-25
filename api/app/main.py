from fastapi import FastAPI

from .ratelimit import RateLimitMiddleware
from .routers import health

# Sin documentación pública: se activará solo en desarrollo.
app = FastAPI(
    title="Sentinel API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(RateLimitMiddleware)


@app.middleware("http")
async def cabeceras_seguras(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Content-Security-Policy", "default-src 'none'")
    if request.url.scheme == "https":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
    return response


app.include_router(health.router)
