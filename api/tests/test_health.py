from fastapi.testclient import TestClient

from app import main
from app.routers import health

client = TestClient(main.app)


def test_health_responde_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_ok_cuando_todo_responde(monkeypatch):
    monkeypatch.setattr(health, "check_database", lambda: True)
    monkeypatch.setattr(health, "check_postgis", lambda: True)
    monkeypatch.setattr(health, "check_redis", lambda: True)
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready_503_si_falla_una_dependencia(monkeypatch):
    monkeypatch.setattr(health, "check_database", lambda: True)
    monkeypatch.setattr(health, "check_postgis", lambda: True)
    monkeypatch.setattr(health, "check_redis", lambda: False)
    r = client.get("/ready")
    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "degraded"
    assert body["checks"]["redis"] is False


def test_documentacion_no_es_publica():
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_cabeceras_de_seguridad():
    r = client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["Referrer-Policy"] == "no-referrer"
    assert r.headers["Content-Security-Policy"] == "default-src 'none'"
    assert "Access-Control-Allow-Origin" not in r.headers
