from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from business.negocio_contribuyente import NegocioContribuyente
from views.schemas import ContribuyenteOut, ContribuyenteRegistro, TokenOut
from views.seguridad import crear_token, obtener_cuit_actual

router = APIRouter(prefix="/auth", tags=["autenticacion"])


@router.get("/me", response_model=ContribuyenteOut)
def perfil(cuit: str = Depends(obtener_cuit_actual), negocio: NegocioContribuyente = Depends(NegocioContribuyente)):
    return negocio.obtener(cuit)


@router.post("/registro", response_model=ContribuyenteOut, status_code=status.HTTP_201_CREATED)
def registrar(datos: ContribuyenteRegistro, negocio: NegocioContribuyente = Depends(NegocioContribuyente)):
    return negocio.registrar(
        datos.cuit, datos.razon_social, datos.condicion_iva, datos.password, datos.confirmacion_password
    )


@router.post("/login", response_model=TokenOut)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    negocio: NegocioContribuyente = Depends(NegocioContribuyente),
):
    """El campo 'username' del formulario OAuth2 estándar se usa como CUIT."""
    contribuyente = negocio.login(form.username, form.password)
    return TokenOut(access_token=crear_token(contribuyente.cuit))
