from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from business.excepciones import (
    CoeficienteInvalido,
    ComprobanteDuplicado,
    ComprobanteInvalido,
    CredencialesInvalidas,
    CuitDuplicado,
    CuitInvalido,
)
from views.routers import auth, comprobantes, libro_iva

app = FastAPI(title="Libro de IVA Digital", description="TPI Integrador - Grupo 2")

app.include_router(auth.router, prefix="/api")
app.include_router(comprobantes.router, prefix="/api")
app.include_router(libro_iva.router, prefix="/api")

# El front (React) vive en TPI/front y se sirve sólo si ya se corrió "npm run build".
# En desarrollo el front corre aparte con Vite (que proxea /api a este servidor).
FRONT_DIST = Path(__file__).resolve().parent.parent.parent / "front" / "dist"

if FRONT_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONT_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def servir_spa(full_path: str) -> FileResponse:
        """Catch-all registrado después de /api/*: deja que React Router maneje la ruta."""
        return FileResponse(FRONT_DIST / "index.html")

_ERRORES_HTTP = {
    CuitInvalido: 400,
    CuitDuplicado: 409,
    CredencialesInvalidas: 401,
    ComprobanteInvalido: 400,
    ComprobanteDuplicado: 409,
    CoeficienteInvalido: 500,
}


def _responder_error_de_negocio(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=_ERRORES_HTTP[type(exc)], content={"detail": str(exc)})


for _excepcion in _ERRORES_HTTP:
    app.add_exception_handler(_excepcion, _responder_error_de_negocio)
