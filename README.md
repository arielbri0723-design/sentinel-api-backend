# Red de alerta: Hito 0 (esqueleto)

## Cómo correrlo en Windows (con Docker Desktop ya funcionando)

1. Abre PowerShell dentro de esta carpeta.
2. Copia la plantilla de variables:   copy .env.example .env
3. Abre .env con el Bloc de notas y cambia las tres contraseñas por claves largas
   (solo letras y números, para no romper las URLs de conexión).
4. Levanta todo:                      docker compose up --build
5. En otra PowerShell comprueba:
   - http://localhost:8000/health  debe responder {"status":"ok"}
   - http://localhost:8000/ready   debe responder status ok con los tres checks en true
6. Para ver la base con pgAdmin (opcional):  docker compose --profile tools up

## Pruebas automáticas
Dentro del contenedor:  docker compose run --rm api python -m pytest -q

## Reglas
- Los puertos solo están abiertos en tu computadora (127.0.0.1).
