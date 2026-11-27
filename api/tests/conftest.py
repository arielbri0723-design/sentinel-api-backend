import os

import pytest
import redis
from sqlalchemy import delete

from app.database import SessionLocal
from app.models.user import User
from app.ratelimit import reset_rate_limits

_PREFIJO_PRUEBA = "auth-test-"
_DOMINIO_PRUEBA = "ejemplo.com"


@pytest.fixture(autouse=True)
def _reiniciar_limite_de_peticiones():
    """Cada test arranca con el contador limpio, sin importar el orden."""
    reset_rate_limits()


def _borrar_usuarios_de_prueba() -> None:
    with SessionLocal() as session:
        session.execute(
            delete(User).where(
                User.email.like(f"{_PREFIJO_PRUEBA}%@{_DOMINIO_PRUEBA}")
            )
        )
        session.commit()


@pytest.fixture
def entorno_auth():
    """Aísla los tests de auth: Redis DB 15 y usuarios de prueba.

    Falla a propósito si REDIS_URL no apunta a la base 15, para no borrar
    nunca el Redis de desarrollo ni el de producción.
    """
    url = os.environ.get("REDIS_URL", "")
    if not url.rstrip("/").endswith("/15"):
        pytest.fail("Los tests de auth necesitan REDIS_URL apuntando a la base 15")

    cliente = redis.Redis.from_url(url)
    cliente.flushdb()
    _borrar_usuarios_de_prueba()
    try:
        yield
    finally:
        cliente.flushdb()
        _borrar_usuarios_de_prueba()
        cliente.close()
