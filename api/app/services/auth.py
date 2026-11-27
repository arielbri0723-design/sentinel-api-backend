"""Reglas de negocio de autenticación."""

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import sessions
from ..models.user import User
from ..security import hash_password, verify_dummy_password, verify_password


class EmailYaRegistradoError(Exception):
    """El email ya tiene una cuenta."""


class CredencialesInvalidasError(Exception):
    """Email inexistente, clave incorrecta o cuenta inactiva."""


class CuentaBloqueadaError(Exception):
    """Demasiados intentos fallidos para esa cuenta."""


def normalizar_email(email: str) -> str:
    return email.strip().lower()


def registrar_usuario(session: Session, email: str, password: str) -> User:
    email = normalizar_email(email)
    if session.scalar(select(User.id).where(User.email == email)) is not None:
        raise EmailYaRegistradoError

    usuario = User(email=email, password_hash=hash_password(password))
    session.add(usuario)
    try:
        session.commit()
    except IntegrityError as exc:
        # Dos registros simultáneos con el mismo email: gana el UNIQUE.
        session.rollback()
        raise EmailYaRegistradoError from exc

    session.refresh(usuario)
    return usuario


def iniciar_sesion(session: Session, email: str, password: str) -> str:
    """Valida las credenciales y devuelve un token de sesión nuevo."""
    email = normalizar_email(email)

    if sessions.esta_bloqueada(email):
        raise CuentaBloqueadaError

    usuario = session.scalar(select(User).where(User.email == email))
    if usuario is None:
        # Mismo costo que una verificación real, para no filtrar por tiempo.
        verify_dummy_password(password)
        sessions.registrar_fallo(email)
        raise CredencialesInvalidasError

    if not verify_password(password, usuario.password_hash) or not usuario.is_active:
        sessions.registrar_fallo(email)
        raise CredencialesInvalidasError

    sessions.limpiar_fallos(email)
    return sessions.crear_sesion(usuario.id)


def cerrar_sesion(token: str) -> None:
    sessions.revocar_sesion(token)


def buscar_usuario(session: Session, usuario_id: uuid.UUID) -> User | None:
    return session.get(User, usuario_id)
