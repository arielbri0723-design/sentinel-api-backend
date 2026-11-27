from app.security import (
    generate_token,
    hash_password,
    hash_token,
    verify_dummy_password,
    verify_password,
)

CLAVE = "clave-de-prueba-123"


def test_hash_argon2id_no_expone_la_clave():
    resultado = hash_password(CLAVE)
    assert resultado != CLAVE
    assert resultado.startswith("$argon2id$")
    assert verify_password(CLAVE, resultado) is True


def test_verify_rechaza_la_clave_incorrecta():
    assert verify_password("otra-clave-distinta", hash_password(CLAVE)) is False


def test_hash_usa_sal_distinta_cada_vez():
    assert hash_password(CLAVE) != hash_password(CLAVE)


def test_token_tiene_entropia_suficiente():
    token = generate_token()
    assert len(token) >= 43
    assert generate_token() != token


def test_hash_token_es_estable_y_de_64_hex():
    token = generate_token()
    assert hash_token(token) == hash_token(token)
    assert len(hash_token(token)) == 64
    assert token not in hash_token(token)


def test_verify_dummy_no_falla():
    verify_dummy_password(CLAVE)
