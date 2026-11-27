import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth import normalizar_email

EMAIL = "persona@ejemplo.com"


@pytest.mark.parametrize("password", ["a" * 11, "a" * 129])
def test_registro_rechaza_largo_invalido(password: str):
    with pytest.raises(ValidationError):
        RegisterRequest(email=EMAIL, password=password)


def test_registro_acepta_12_caracteres():
    assert RegisterRequest(email=EMAIL, password="a" * 12).password == "a" * 12


def test_registro_rechaza_email_invalido():
    with pytest.raises(ValidationError):
        RegisterRequest(email="no-es-un-email", password="a" * 12)


def test_login_acepta_clave_corta():
    """En login una clave corta debe dar 401, no un 422 que revele la política."""
    assert LoginRequest(email=EMAIL, password="x").password == "x"


def test_email_se_normaliza():
    assert normalizar_email("  Persona@Ejemplo.COM ") == "persona@ejemplo.com"
