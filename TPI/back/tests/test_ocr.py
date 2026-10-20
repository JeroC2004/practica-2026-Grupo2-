from business.ocr import parsear_texto_comprobante

TEXTO_FACTURA_A = """
FACTURA
A
COD. 01
Punto de Venta: 0001        Comp. Nro: 00000123
Fecha de Emisión: 15/03/2026
CUIT: 30-71234567-3
Razón Social: Proveedor SRL

Neto Gravado $      10.000,00
IVA 21%       $       2.100,00
Importe Total $      12.100,00
"""

TEXTO_NOTA_CREDITO_B = """
NOTA DE CREDITO
B
Punto de Venta: 0005        Comp. Nro: 00009999
Fecha de Emisión: 01/12/2026
CUIT: 20-30405060-7

Neto Gravado $ 500,00
Importe Exento $ 0,00
IVA $ 105,00
Importe Total $ 605,00
"""


def test_detecta_cuit_punto_de_venta_y_numero():
    resultado = parsear_texto_comprobante(TEXTO_FACTURA_A)

    assert resultado["cuit_contraparte"] == "30712345673"
    assert resultado["punto_venta"] == 1
    assert resultado["numero"] == 123


def test_detecta_tipo_de_comprobante_factura():
    resultado = parsear_texto_comprobante(TEXTO_FACTURA_A)

    assert resultado["tipo"] == "A"


def test_detecta_tipo_nota_de_credito():
    resultado = parsear_texto_comprobante(TEXTO_NOTA_CREDITO_B)

    assert resultado["tipo"] == "NC"


def test_detecta_fecha_en_formato_argentino():
    resultado = parsear_texto_comprobante(TEXTO_FACTURA_A)

    assert resultado["fecha"] == "2026-03-15"


def test_detecta_importes_con_formato_de_miles_argentino():
    resultado = parsear_texto_comprobante(TEXTO_FACTURA_A)

    assert resultado["neto_gravado"] == 10_000.0
    assert resultado["iva"] == 2_100.0
    assert resultado["total"] == 12_100.0


def test_detecta_importes_chicos_sin_separador_de_miles():
    resultado = parsear_texto_comprobante(TEXTO_NOTA_CREDITO_B)

    assert resultado["neto_gravado"] == 500.0
    assert resultado["neto_exento"] == 0.0
    assert resultado["iva"] == 105.0
    assert resultado["total"] == 605.0


def test_no_confunde_la_condicion_de_ingresos_brutos_con_el_neto_exento():
    # "Ingresos Brutos: Exento" es una condición impositiva del emisor, no un
    # importe — no debe confundirse con la línea real "Importe Exento".
    texto = (
        "Ingresos Brutos: Exento Comp. Nro: 00000050\n"
        "Importe Neto Gravado $ 1.000,00\n"
        "Importe Exento $ 0,00\n"
    )

    resultado = parsear_texto_comprobante(texto)

    assert resultado["neto_exento"] == 0.0


def test_detecta_importes_cuando_el_ocr_confunde_la_coma_decimal_con_un_punto():
    # Tesseract a veces lee "1.000,00" como "1.000.00" (confunde la coma con
    # un punto). Debe interpretarse igual que el formato correcto.
    texto = "Importe Neto Gravado $ 1.000.00\nIVA 21% $ 210.00\nImporte Total $ 1.210.00"

    resultado = parsear_texto_comprobante(texto)

    assert resultado["neto_gravado"] == 1_000.0
    assert resultado["iva"] == 210.0
    assert resultado["total"] == 1_210.0


def test_texto_sin_datos_reconocibles_devuelve_todo_none():
    resultado = parsear_texto_comprobante("texto ilegible sin ningun dato util")

    assert resultado["cuit_contraparte"] is None
    assert resultado["punto_venta"] is None
    assert resultado["tipo"] is None
    assert resultado["fecha"] is None
    assert resultado["total"] is None
