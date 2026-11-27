from app.database import _normalizar_url


def test_normaliza_url_para_psycopg():
    assert (
        _normalizar_url("postgresql://u:p@h/db")
        == "postgresql+psycopg://u:p@h/db"
    )
    assert (
        _normalizar_url("postgres://u:p@h/db")
        == "postgresql+psycopg://u:p@h/db"
    )
    assert (
        _normalizar_url("postgresql+psycopg://u:p@h/db")
        == "postgresql+psycopg://u:p@h/db"
    )
