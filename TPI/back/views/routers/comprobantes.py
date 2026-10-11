from fastapi import APIRouter, Depends, status

from business.modelos import CondicionComprobante, Comprobante, OrigenComprobante
from business.negocio_comprobante import NegocioComprobante
from views.schemas import ComprobanteIn, ComprobanteOut
from views.seguridad import obtener_cuit_actual

router = APIRouter(prefix="/comprobantes", tags=["comprobantes"])


@router.post("", response_model=ComprobanteOut, status_code=status.HTTP_201_CREATED)
def cargar_comprobante(
    datos: ComprobanteIn,
    cuit: str = Depends(obtener_cuit_actual),
    negocio: NegocioComprobante = Depends(NegocioComprobante),
):
    comprobante = Comprobante(cuit_contribuyente=cuit, origen=OrigenComprobante.MANUAL, **datos.model_dump())
    return negocio.alta(comprobante)


@router.get("", response_model=list[ComprobanteOut])
def listar_comprobantes(
    condicion: CondicionComprobante,
    mes: int,
    anio: int,
    cuit: str = Depends(obtener_cuit_actual),
    negocio: NegocioComprobante = Depends(NegocioComprobante),
):
    return negocio.listar_por_mes(cuit, condicion, mes, anio)
