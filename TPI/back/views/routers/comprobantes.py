from fastapi import APIRouter, Depends, File, UploadFile, status

from business import ocr
from business.modelos import CondicionComprobante, Comprobante, OrigenComprobante
from business.negocio_arca import NegocioArca
from business.negocio_comprobante import NegocioComprobante
from views.schemas import ComprobanteIn, ComprobanteOcrOut, ComprobanteOut
from views.seguridad import obtener_cuit_actual

router = APIRouter(prefix="/comprobantes", tags=["comprobantes"])


@router.post("/ocr", response_model=ComprobanteOcrOut)
async def reconocer_comprobante(archivo: UploadFile = File(...), cuit: str = Depends(obtener_cuit_actual)):
    """Analiza la foto de un comprobante y devuelve los campos detectados, sin guardarlos."""
    contenido = await archivo.read()
    return ocr.reconocer_comprobante(contenido)


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


@router.post("/{comprobante_id}/emitir-arca", response_model=ComprobanteOut)
def emitir_en_arca(
    comprobante_id: int,
    cuit: str = Depends(obtener_cuit_actual),
    negocio: NegocioArca = Depends(NegocioArca),
):
    return negocio.emitir(cuit, comprobante_id)
