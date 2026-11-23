from fastapi import APIRouter, Response

from ..cache import check_redis
from ..db import check_database, check_postgis

router = APIRouter(tags=["operación"])


@router.get("/health")
def health():
    """Vivo: el proceso responde. No toca la base ni Redis."""
    return {"status": "ok"}


@router.get("/ready")
def ready(response: Response):
    """Listo: las dependencias responden. Devuelve 503 si alguna falla.

    Solo devuelve verdadero o falso por componente: no se filtran detalles internos.
    """
    checks = {
        "database": check_database(),
        "postgis": check_postgis(),
        "redis": check_redis(),
    }
    ok = all(checks.values())
    if not ok:
        response.status_code = 503
    return {"status": "ok" if ok else "degraded", "checks": checks}
