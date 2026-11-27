"""Endpoints de registro, login, logout y perfil."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import sessions
from ..database import get_session
from ..dependencies import get_current_user, get_token
from ..models.user import User
from ..schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from ..services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar(
    payload: RegisterRequest,
    session: Session = Depends(get_session),
) -> User:
    try:
        return auth_service.registrar_usuario(session, payload.email, payload.password)
    except auth_service.EmailYaRegistradoError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    session: Session = Depends(get_session),
) -> TokenResponse:
    try:
        token = auth_service.iniciar_sesion(session, payload.email, payload.password)
    except auth_service.CuentaBloqueadaError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos",
            headers={"Retry-After": str(sessions.LOCKOUT_TTL_SECONDS)},
        )
    except auth_service.CredencialesInvalidasError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=token,
        expires_in=sessions.SESSION_TTL_SECONDS,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    token: str = Depends(get_token),
    _usuario: User = Depends(get_current_user),
) -> Response:
    auth_service.cerrar_sesion(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
def perfil(usuario: User = Depends(get_current_user)) -> User:
    return usuario
