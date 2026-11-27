FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv

# El usuario existe antes de los COPY para poder usarlo como dueño de los
# archivos: si /srv queda de root, pytest no puede escribir su caché y avisa
# "Permission denied" en cada corrida. El chown de /srv es porque pytest crea
# el directorio de caché ahí, no solo dentro de app/ y tests/.
RUN useradd --create-home appuser && chown appuser:appuser /srv

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser tests ./tests
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser migrations ./migrations
COPY --chown=appuser:appuser pytest.ini .

# No correr como administrador dentro del contenedor
USER appuser

# Sin curl en la imagen: urllib de la stdlib alcanza para el liveness.
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
