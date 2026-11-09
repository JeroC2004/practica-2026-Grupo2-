from fastapi import APIRouter, Depends, Path

from business.negocio_estadisticas import NegocioEstadisticas
from views.schemas import EstadisticasOut
from views.seguridad import obtener_cuit_actual

router = APIRouter(prefix="/estadisticas", tags=["estadisticas"])


@router.get("/{anio}", response_model=EstadisticasOut)
def obtener_estadisticas(
    anio: int = Path(ge=1, le=9998),
    cuit: str = Depends(obtener_cuit_actual),
    negocio: NegocioEstadisticas = Depends(NegocioEstadisticas),
):
    return negocio.consultar(cuit, anio)
