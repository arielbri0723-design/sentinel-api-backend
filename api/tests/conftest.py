import pytest

from app.ratelimit import reset_rate_limits


@pytest.fixture(autouse=True)
def _reiniciar_limite_de_peticiones():
    """Cada test arranca con el contador limpio, sin importar el orden."""
    reset_rate_limits()
