import os
import re
from datetime import date

import cv2
import numpy as np
import pytesseract

TESSERACT_LANG = os.environ.get("TESSERACT_LANG", "eng")

# Ruta default del instalador de UB-Mannheim (winget/instalador oficial para Windows).
# TESSERACT_CMD permite overridearla si Tesseract está en otro lado.
_TESSERACT_CMD_WINDOWS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.environ.get("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]
elif os.name == "nt" and os.path.exists(_TESSERACT_CMD_WINDOWS):
    pytesseract.pytesseract.tesseract_cmd = _TESSERACT_CMD_WINDOWS

_NUMERO_AR = r"[\d.,]+"
_CUIT_REGEX = re.compile(r"\b(\d{2})-?(\d{8})-?(\d)\b")
_COMPROBANTE_REGEX = re.compile(r"\b(\d{4,5})-(\d{8})\b")
_PUNTO_VENTA_REGEX = re.compile(r"Punto\s*de\s*Venta[:\s]*(\d{4,5})", re.IGNORECASE)
_NUMERO_COMPROBANTE_REGEX = re.compile(r"Comp\.?\s*Nro[.:\s]*(\d{1,8})", re.IGNORECASE)
_FECHA_REGEX = re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b")
_TIPO_REGEX = re.compile(r"(FACTURA|NOTA\s+DE\s+CR[EÉ]DITO|NOTA\s+DE\s+D[EÉ]BITO)[^A-Z0-9]{0,20}?([ABC])\b")


def _a_float(texto: str) -> float | None:
    """
    Convierte un importe reconocido por OCR a float. El formato esperado es
    argentino ("1.000,00"), pero Tesseract a veces confunde la "," decimal con
    un "." (queda "1.000.00") — se asume que el ÚLTIMO separador seguido de
    exactamente 2 dígitos es el decimal, y el resto son separadores de miles.
    """
    texto = texto.strip()
    if not texto:
        return None

    decimal = re.search(r"[.,](\d{2})$", texto)
    if decimal:
        parte_entera = re.sub(r"[.,]", "", texto[: decimal.start()]) or "0"
        texto = f"{parte_entera}.{decimal.group(1)}"
    else:
        texto = re.sub(r"[.,]", "", texto)

    try:
        return float(texto)
    except ValueError:
        return None


def _buscar_importe(texto: str, etiqueta: str) -> float | None:
    coincidencia = re.search(rf"{etiqueta}[^\d\n]{{0,15}}({_NUMERO_AR})", texto, re.IGNORECASE)
    return _a_float(coincidencia.group(1)) if coincidencia else None


def parsear_texto_comprobante(texto: str) -> dict:
    """
    Extrae por regex los campos de un comprobante a partir del texto ya
    reconocido por OCR. Los campos que no se detectan quedan en None: el
    usuario los completa o corrige a mano antes de confirmar la carga, ya que
    el OCR sobre fotos reales nunca es 100% preciso.
    """
    resultado: dict = {
        "tipo": None,
        "punto_venta": None,
        "numero": None,
        "fecha": None,
        "cuit_contraparte": None,
        "neto_gravado": _buscar_importe(texto, r"Neto\s*Grav(?:ado)?"),
        # "Importe" es obligatorio en el regex: una palabra suelta "Exento" también
        # aparece en encabezados como "Ingresos Brutos: Exento" (una condición
        # impositiva, no un importe), y sin esto se terminaba leyendo cualquier
        # número cercano a esa palabra como si fuera el neto exento.
        "neto_exento": _buscar_importe(texto, r"Importe\s+Exento"),
        "iva": _buscar_importe(texto, r"IVA(?:\s*\d+%)?"),
        "total": _buscar_importe(texto, r"(?:Importe\s*)?Total"),
    }

    cuit = _CUIT_REGEX.search(texto)
    if cuit:
        resultado["cuit_contraparte"] = "".join(cuit.groups())

    comprobante = _COMPROBANTE_REGEX.search(texto)
    if comprobante:
        resultado["punto_venta"] = int(comprobante.group(1))
        resultado["numero"] = int(comprobante.group(2))
    else:
        # Algunos comprobantes imprimen punto de venta y número por separado
        # (con sus propias etiquetas) en vez de "0001-00000123" junto.
        punto_venta = _PUNTO_VENTA_REGEX.search(texto)
        numero = _NUMERO_COMPROBANTE_REGEX.search(texto)
        if punto_venta:
            resultado["punto_venta"] = int(punto_venta.group(1))
        if numero:
            resultado["numero"] = int(numero.group(1))

    fecha = _FECHA_REGEX.search(texto)
    if fecha:
        dia, mes, anio = (int(parte) for parte in fecha.groups())
        try:
            resultado["fecha"] = date(anio, mes, dia).isoformat()
        except ValueError:
            pass

    tipo = _TIPO_REGEX.search(texto.upper())
    if tipo:
        etiqueta, letra = tipo.group(1), tipo.group(2)
        if etiqueta.startswith("NOTA"):
            resultado["tipo"] = "NC" if "CR" in etiqueta else "ND"
        else:
            resultado["tipo"] = letra

    return resultado


def _preprocesar(imagen_bytes: bytes) -> np.ndarray:
    arreglo = np.frombuffer(imagen_bytes, dtype=np.uint8)
    imagen = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    return cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11)


def reconocer_comprobante(imagen_bytes: bytes) -> dict:
    """Corre OCR sobre la foto de un comprobante y devuelve los campos detectados."""
    texto = pytesseract.image_to_string(_preprocesar(imagen_bytes), lang=TESSERACT_LANG)
    return parsear_texto_comprobante(texto)
