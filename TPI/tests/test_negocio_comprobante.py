from datetime import date

import pytest

from business.excepciones import ComprobanteDuplicado, ComprobanteInvalido
from business.modelos import Comprobante, TipoComprobante, CondicionComprobante
from business.negocio_comprobante import NegocioComprobante


class FakeDatosComprobante:
    def __init__(self, existente=None):
        self.existente = existente
        self.dados_de_alta = []

    def buscar_por_clave(self, cuit_contribuyente, tipo, punto_venta, numero, condicion):
        return self.existente

    def alta(self, comprobante):
        self.dados_de_alta.append(comprobante)
        comprobante.id = len(self.dados_de_alta)
        return comprobante


def comprobante_valido(**overrides):
    base = dict(
        cuit_contribuyente="20304050607",
        tipo=TipoComprobante.FACTURA_A,
        punto_venta=1,
        numero=100,
        fecha=date(2026, 3, 15),
        cuit_contraparte="30111222334",
        neto_gravado=1000.0,
        neto_exento=0.0,
        iva=210.0,
        total=1210.0,
        condicion=CondicionComprobante.COMPRA,
    )
    base.update(overrides)
    return Comprobante(**base)


def test_alta_de_comprobante_valido_lo_persiste():
    datos = FakeDatosComprobante()
    negocio = NegocioComprobante(datos=datos)

    resultado = negocio.alta(comprobante_valido())

    assert resultado.id == 1
    assert datos.dados_de_alta == [resultado]


def test_no_permite_cargar_un_comprobante_duplicado():
    datos = FakeDatosComprobante(existente=comprobante_valido())
    negocio = NegocioComprobante(datos=datos)

    with pytest.raises(ComprobanteDuplicado):
        negocio.alta(comprobante_valido())


def test_no_permite_importes_negativos():
    datos = FakeDatosComprobante()
    negocio = NegocioComprobante(datos=datos)

    with pytest.raises(ComprobanteInvalido):
        negocio.alta(comprobante_valido(neto_gravado=-1000.0))


def test_no_permite_total_inconsistente_con_los_netos_y_el_iva():
    datos = FakeDatosComprobante()
    negocio = NegocioComprobante(datos=datos)

    with pytest.raises(ComprobanteInvalido):
        negocio.alta(comprobante_valido(total=9999.0))


def test_tolera_pequenas_diferencias_de_redondeo_en_el_total():
    datos = FakeDatosComprobante()
    negocio = NegocioComprobante(datos=datos)

    resultado = negocio.alta(comprobante_valido(total=1210.004))

    assert resultado.total == 1210.004
