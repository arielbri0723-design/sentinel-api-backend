"""El límite de peticiones se aplica sin depender de infraestructura."""

from fastapi.testclient import TestClient

from app import main
from app.routers import health

client = TestClient(main.app)


def test_ready_se_limita_despues_de_30_peticiones(monkeypatch):
    monkeypatch.setattr(health, "check_database", lambda: True)
    monkeypatch.setattr(health, "check_postgis", lambda: True)
    monkeypatch.setattr(health, "check_redis", lambda: True)

    for _ in range(30):
        assert client.get("/ready").status_code == 200

    respuesta = client.get("/ready")
    assert respuesta.status_code == 429
    assert respuesta.json() == {"detail": "Demasiadas peticiones"}
    assert int(respuesta.headers["Retry-After"]) > 0


def test_health_no_cuenta_para_el_mismo_limite(monkeypatch):
    monkeypatch.setattr(health, "check_database", lambda: True)
    monkeypatch.setattr(health, "check_postgis", lambda: True)
    monkeypatch.setattr(health, "check_redis", lambda: True)

    for _ in range(30):
        assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
