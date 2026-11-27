from app.models import User


def test_email_se_normaliza_a_minusculas():
    user = User(email="  Ariel@Example.COM ", password_hash="hash-de-prueba")
    assert user.email == "ariel@example.com"
