"""Tests de integración de autenticación.

Necesitan Postgres y Redis reales y se ejecutan en el servicio `migrate`,
que tiene la URL de la API y la base de tests. El fixture `entorno_auth`
limpia Redis DB 15 y los usuarios creados por estos tests.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ratelimit import reset_rate_limits

pytestmark = pytest.mark.integration

PASSWORD = "clave-de-prueba-123"


def _email() -> str:
    return f"auth-test-{uuid.uuid4().hex}@ejemplo.com"


@pytest.fixture
def cliente(entorno_auth) -> TestClient:
    return TestClient(app)


def _registrar(cliente: TestClient, email: str, password: str = PASSWORD):
    return cliente.post(
        "/auth/register",
        json={"email": email, "password": password},
    )


def _login(cliente: TestClient, email: str, password: str = PASSWORD):
    return cliente.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


def test_registro_exitoso(cliente: TestClient):
    email = _email()
    respuesta = _registrar(cliente, email)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["email"] == email
    assert cuerpo["is_active"] is True
    assert "id" in cuerpo
    assert "created_at" in cuerpo
    assert "password_hash" not in cuerpo


def test_registro_duplicado_ignora_mayusculas(cliente: TestClient):
    email = _email()
    assert _registrar(cliente, email).status_code == 201

    respuesta = _registrar(cliente, email.upper())

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "El email ya está registrado"}


def test_login_correcto_devuelve_token(cliente: TestClient):
    email = _email()
    _registrar(cliente, email)

    respuesta = _login(cliente, email)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["expires_in"] == 60 * 60 * 24 * 7
    assert len(cuerpo["access_token"]) >= 43
    assert "password_hash" not in cuerpo


def test_login_con_clave_incorrecta(cliente: TestClient):
    email = _email()
    _registrar(cliente, email)

    respuesta = _login(cliente, email, "clave-equivocada-123")

    assert respuesta.status_code == 401
    assert respuesta.headers["WWW-Authenticate"] == "Bearer"


def test_login_de_usuario_inexistente_no_filtra_informacion(cliente: TestClient):
    email = _email()

    inexistente = _login(cliente, email)
    existente = _registrar(cliente, _email())
    assert existente.status_code == 201
    clave_incorrecta = _login(cliente, existente.json()["email"], "otra-clave-123")

    assert inexistente.status_code == clave_incorrecta.status_code == 401
    assert inexistente.json() == clave_incorrecta.json()


def test_me_sin_token(cliente: TestClient):
    respuesta = cliente.get("/auth/me")

    assert respuesta.status_code == 401
    assert respuesta.headers["WWW-Authenticate"] == "Bearer"


def test_me_con_token(cliente: TestClient):
    email = _email()
    _registrar(cliente, email)
    token = _login(cliente, email).json()["access_token"]

    respuesta = cliente.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == email
    assert "password_hash" not in respuesta.json()


def test_logout_invalida_el_token(cliente: TestClient):
    email = _email()
    _registrar(cliente, email)
    token = _login(cliente, email).json()["access_token"]
    cabecera = {"Authorization": f"Bearer {token}"}

    assert cliente.post("/auth/logout", headers=cabecera).status_code == 204
    assert cliente.get("/auth/me", headers=cabecera).status_code == 401


def test_bloqueo_por_cuenta_aunque_cambie_la_ip(cliente: TestClient):
    email = _email()
    assert _registrar(cliente, email).status_code == 201

    for _ in range(5):
        assert _login(cliente, email, "clave-equivocada-123").status_code == 401

    # El límite por IP es en memoria y por proceso: reiniciarlo equivale a
    # llegar desde otra IP. El contador de la cuenta vive en Redis y sigue.
    reset_rate_limits()

    respuesta = _login(cliente, email)

    assert respuesta.status_code == 429
    assert respuesta.headers["Retry-After"] == str(15 * 60)
