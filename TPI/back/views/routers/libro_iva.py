from fastapi import APIRouter, Depends

from business.negocio_libro_iva import NegocioLibroIva
from views.schemas import LibroIvaOut
from views.seguridad import obtener_cuit_actual

router = APIRouter(prefix="/libro-iva", tags=["libro-iva"])


@router.get("/{anio}/{mes}", response_model=LibroIvaOut)
def obtener_libro_iva(
    anio: int,
    mes: int,
    cuit: str = Depends(obtener_cuit_actual),
    negocio: NegocioLibroIva = Depends(NegocioLibroIva),
):
    return negocio.armar_libro_iva(cuit, mes, anio)
