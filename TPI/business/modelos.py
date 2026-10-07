from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class CondicionIva(str, Enum):
    MONOTRIBUTO = "monotributo"
    RESPONSABLE_INSCRIPTO = "responsable_inscripto"


class TipoComprobante(str, Enum):
    FACTURA_A = "A"
    FACTURA_B = "B"
    FACTURA_C = "C"
    NOTA_CREDITO = "NC"
    NOTA_DEBITO = "ND"


class CondicionComprobante(str, Enum):
    COMPRA = "compra"
    VENTA = "venta"


class OrigenComprobante(str, Enum):
    MANUAL = "manual"
    OCR = "ocr"
    ARCA = "arca"


@dataclass
class Contribuyente:
    cuit: str
    razon_social: str
    condicion_iva: CondicionIva
    password_hash: str = ""
    id: int = None


@dataclass
class Comprobante:
    cuit_contribuyente: str
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
    origen: OrigenComprobante = OrigenComprobante.MANUAL
    id: int = None


@dataclass
class ResultadoLibroIva:
    cuit_contribuyente: str
    mes: int
    anio: int
    compras: list = field(default_factory=list)
    ventas: list = field(default_factory=list)
    coeficiente_prorrateo: float = 1.0
    credito_fiscal_computable: float = 0.0
