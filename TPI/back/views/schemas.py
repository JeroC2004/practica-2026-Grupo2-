from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from business.modelos import CondicionComprobante, CondicionIva, TipoComprobante


class ContribuyenteRegistro(BaseModel):
    cuit: str = Field(min_length=11, max_length=11, description="11 dígitos, sin guiones")
    razon_social: str = Field(min_length=1)
    condicion_iva: CondicionIva
    password: str = Field(min_length=6)


class ContribuyenteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cuit: str
    razon_social: str
    condicion_iva: CondicionIva


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ComprobanteIn(BaseModel):
    tipo: TipoComprobante
    punto_venta: int = Field(gt=0)
    numero: int = Field(gt=0)
    fecha: date
    cuit_contraparte: str = Field(min_length=11, max_length=11)
    neto_gravado: float = Field(ge=0)
    neto_exento: float = Field(ge=0)
    iva: float = Field(ge=0)
    total: float = Field(ge=0)
    condicion: CondicionComprobante


class ComprobanteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoComprobante
    punto_venta: int
    numero: int
    fecha: date
    cuit_contraparte: str
    neto_gravado: float
    neto_exento: float
    iva: float
    total: float
    condicion: CondicionComprobante
    origen: str


class LibroIvaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cuit_contribuyente: str
    mes: int
    anio: int
    compras: list[ComprobanteOut]
    ventas: list[ComprobanteOut]
    coeficiente_prorrateo: float
    credito_fiscal_computable: float
