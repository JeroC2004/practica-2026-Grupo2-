from fastapi import APIRouter, Depends

from business.negocio_arca import NegocioArca
from views.schemas import EstadoArca, EstadoCompraArca
from views.seguridad import obtener_cuit_actual

router = APIRouter(prefix="/validacion-arca", tags=["validacion-arca"])


@router.get("/compras/{anio}/{mes}", response_model=list[EstadoCompraArca])
def validar_compras_mes(
    anio: int,
    mes: int,
    cuit: str = Depends(obtener_cuit_actual),
    negocio: NegocioArca = Depends(NegocioArca),
):
    return negocio.validar_compras_mes(cuit, mes, anio)


@router.get("/{anio}/{mes}", response_model=list[EstadoArca])
def validar_mes(
    anio: int,
    mes: int,
    cuit: str = Depends(obtener_cuit_actual),
    negocio: NegocioArca = Depends(NegocioArca),
):
    return negocio.validar_mes(cuit, mes, anio)
