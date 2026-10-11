import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header, HTTPException, status

ALGORITMO = "HS256"
EXPIRACION_MINUTOS = 60
SECRET_KEY = os.environ.get("JWT_SECRET", "clave-de-desarrollo-no-usar-en-produccion")


def crear_token(cuit: str) -> str:
    """Genera un JWT firmado cuyo 'sub' es el CUIT del contribuyente autenticado."""
    expira = datetime.now(timezone.utc) + timedelta(minutes=EXPIRACION_MINUTOS)
    return jwt.encode({"sub": cuit, "exp": expira}, SECRET_KEY, algorithm=ALGORITMO)


def _decodificar(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
    except jwt.PyJWTError as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido o expirado.") from error
    return payload["sub"]


def obtener_cuit_actual(authorization: str | None = Header(default=None)) -> str:
    """
    Dependency de FastAPI: exige un CUIT autenticado vía ``Authorization: Bearer``.
    No se guarda ningún estado en el servidor: todo viaja en el token.
    """
    token = authorization.removeprefix("Bearer ") if authorization else None
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No autenticado.")
    return _decodificar(token)
