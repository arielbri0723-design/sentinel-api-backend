"""Límite de peticiones por IP y ruta, en memoria y por proceso."""

import threading
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Registro global para poder vacuumiar el estado desde los tests.
_limiters: list["RateLimitMiddleware"] = []


def reset_rate_limits() -> None:
    """Borra el historial de peticiones. Solo se usa en los tests."""
    for limiter in _limiters:
        with limiter.lock:
            limiter.hits.clear()


def limpiar_historial(limiter: "RateLimitMiddleware") -> None:
    """Descarta ventanas vencidas para que el dict no crezca sin límite."""
    now = time.monotonic()
    for key, history in list(limiter.hits.items()):
        while history and now - history[0] >= limiter.window_seconds:
            history.popleft()
        if not history:
            del limiter.hits[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """ ventana deslizante por (IP, ruta): /ready y /auth/login son estrictos. """

    LIMITS = {
        "/ready": (30, 60),
        "/auth/login": (5, 900),
        "/auth/register": (5, 900),
    }
    DEFAULT = (120, 60)

    def __init__(self, app):
        super().__init__(app)
        self.max_requests: int
        self.window_seconds: int
        self.hits: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()
        _limiters.append(self)

    async def dispatch(self, request: Request, call_next):
        max_requests, window_seconds = self.LIMITS.get(request.url.path, self.DEFAULT)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        ip = request.client.host if request.client else "unknown"
        key = (ip, request.url.path)
        now = time.monotonic()

        with self.lock:
            history = self.hits[key]
            while history and now - history[0] >= window_seconds:
                history.popleft()
            if len(history) >= max_requests:
                retry = max(1, int(window_seconds - (now - history[0])))
                return JSONResponse(
                    {"detail": "Demasiadas peticiones"},
                    status_code=429,
                    headers={"Retry-After": str(retry)},
                )
            history.append(now)
            if len(self.hits) > 1000:
                limpiar_historial(self)

        return await call_next(request)
