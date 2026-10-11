from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from business.negocio_contribuyente import NegocioContribuyente
from views.schemas import ContribuyenteOut, ContribuyenteRegistro, TokenOut
from views.seguridad import crear_token

router = APIRouter(prefix="/auth", tags=["autenticacion"])


@router.post("/registro", response_model=ContribuyenteOut, status_code=status.HTTP_201_CREATED)
def registrar(datos: ContribuyenteRegistro, negocio: NegocioContribuyente = Depends(NegocioContribuyente)):
    return negocio.registrar(datos.cuit, datos.razon_social, datos.condicion_iva, datos.password)


@router.post("/login", response_model=TokenOut)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    negocio: NegocioContribuyente = Depends(NegocioContribuyente),
):
    """El campo 'username' del formulario OAuth2 estándar se usa como CUIT."""
    contribuyente = negocio.login(form.username, form.password)
    return TokenOut(access_token=crear_token(contribuyente.cuit))
