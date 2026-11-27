"""Primitivas de seguridad: hash de contraseñas y tokens opacos.

Las contraseñas se hashean con Argon2id. Los tokens de sesión son valores
aleatorios y en Redis solo se guarda su SHA-256, nunca el token en claro.
"""

import hashlib
import secrets

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Solo Argon2id: no se acepta bcrypt ni otro algoritmo por configuración.
_hasher = PasswordHash((Argon2Hasher(),))

# Hash señuelo: se genera una vez al importar el módulo. Sirve para que un
# login con un email inexistente cueste lo mismo que uno con clave incorrecta.
_HASH_SENUELO = _hasher.hash(secrets.token_urlsafe(32))


def hash_password(password: str) -> str:
    """Devuelve el hash Argon2id de la contraseña."""
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Compara la contraseña con su hash en tiempo constante."""
    return _hasher.verify(password, password_hash)


def verify_dummy_password(password: str) -> None:
    """Consume el mismo tiempo que una verificación real.

    Se usa cuando el email no existe, para no filtrar por tiempos de
    respuesta si la cuenta está registrada. El resultado se descarta.
    """
    _hasher.verify(password, _HASH_SENUELO)


def generate_token() -> str:
    """Token opaco de sesión con 256 bits de entropía."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """SHA-256 hexadecimal del token, que es lo único que se guarda."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
