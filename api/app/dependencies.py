"""Dependencias de FastAPI para autenticación."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from . import sessions
from .database import get_session
from .models.user import User

_bearer = HTTPBearer(auto_error=False)


def _no_autenticado() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    if credentials is None:
        raise _no_autenticado()
    return credentials.credentials


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: Session = Depends(get_session),
) -> User:
    if credentials is None:
        raise _no_autenticado()

    usuario_id = sessions.obtener_usuario_de_sesion(credentials.credentials)
    if usuario_id is None:
        raise _no_autenticado()

    usuario = session.get(User, usuario_id)
    if usuario is None or not usuario.is_active:
        raise _no_autenticado()
    return usuario
