"""Sesiones opacas y bloqueo de cuentas, guardados en Redis.

En Redis se guarda el SHA-256 del token, nunca el token en claro. El bloqueo
por cuenta se aplica a todos los emails, existan o no, para no revelar si una
cuenta está registrada.
"""

import hashlib
import uuid

from redis import Redis

from .cache import get_redis
from .security import generate_token, hash_token

SESSION_TTL_SECONDS = 60 * 60 * 24 * 7
LOCKOUT_MAX_INTENTOS = 5
LOCKOUT_TTL_SECONDS = 15 * 60


def _clave_sesion(token: str) -> str:
    return f"session:{hash_token(token)}"


def _clave_fallos(email: str) -> str:
    # El email ya viene normalizado; se hashea para no guardar datos personales.
    digest = hashlib.sha256(email.encode("utf-8")).hexdigest()
    return f"login:fail:{digest}"


def _cliente() -> Redis:
    return get_redis()


def crear_sesion(usuario_id: uuid.UUID) -> str:
    """Crea una sesión y devuelve el token que recibe el cliente."""
    token = generate_token()
    _cliente().set(_clave_sesion(token), str(usuario_id), ex=SESSION_TTL_SECONDS)
    return token


def obtener_usuario_de_sesion(token: str) -> uuid.UUID | None:
    """Devuelve el UUID del usuario dueño del token, o None si no existe."""
    valor = _cliente().get(_clave_sesion(token))
    if valor is None:
        return None
    texto = valor.decode("utf-8") if isinstance(valor, bytes) else str(valor)
    try:
        return uuid.UUID(texto)
    except ValueError:
        return None


def revocar_sesion(token: str) -> None:
    _cliente().delete(_clave_sesion(token))


def registrar_fallo(email: str) -> int:
    """Suma un intento fallido y devuelve el total de la ventana."""
    cliente = _cliente()
    clave = _clave_fallos(email)
    intentos = int(cliente.incr(clave))
    if intentos == 1:
        cliente.expire(clave, LOCKOUT_TTL_SECONDS)
    return intentos


def esta_bloqueada(email: str) -> bool:
    valor = _cliente().get(_clave_fallos(email))
    if valor is None:
        return False
    texto = valor.decode("utf-8") if isinstance(valor, bytes) else str(valor)
    return int(texto) >= LOCKOUT_MAX_INTENTOS


def limpiar_fallos(email: str) -> None:
    _cliente().delete(_clave_fallos(email))
