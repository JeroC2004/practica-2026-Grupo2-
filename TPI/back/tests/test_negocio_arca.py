from datetime import date

import pytest

from business.excepciones import EmisionArcaInvalida, EmisionArcaRechazada
from business.modelos import Comprobante, CondicionComprobante, TipoComprobante
from business.negocio_arca import NegocioArca

CUIT = "20304050607"


def comprobante_valido(**overrides):
    base = dict(
        id=1,
        cuit_contribuyente=CUIT,
        tipo=TipoComprobante.FACTURA_B,
        punto_venta=1,
        numero=100,
        fecha=date(2026, 3, 15),
        cuit_contraparte="30111222334",
        neto_gravado=1000.0,
        neto_exento=0.0,
        iva=210.0,
        total=1210.0,
        condicion=CondicionComprobante.VENTA,
    )
    base.update(overrides)
    return Comprobante(**base)


class FakeArcaCliente:
    def __init__(self, resultado_emitir=None, excepcion_emitir=None, resultados_consultar=None):
        self.resultado_emitir = resultado_emitir or {
            "numero_arca": 555,
            "cae": "86410988122530",
            "cae_vencimiento": date(2026, 10, 22),
        }
        self.excepcion_emitir = excepcion_emitir
        self.resultados_consultar = resultados_consultar or {}
        self.llamadas_emitir = []

    def emitir(self, tipo, fecha, total, neto_gravado, iva):
        self.llamadas_emitir.append((tipo, fecha, total, neto_gravado, iva))
        if self.excepcion_emitir:
            raise self.excepcion_emitir
        return self.resultado_emitir

    def consultar(self, tipo, numero):
        return self.resultados_consultar.get(numero)


class FakeNegocioComprobante:
    def __init__(self, comprobantes=None):
        self.comprobantes = {c.id: c for c in (comprobantes or [])}

    def obtener(self, comprobante_id):
        return self.comprobantes.get(comprobante_id)

    def listar_por_mes(self, cuit_contribuyente, condicion, mes, anio):
        return [
            c
            for c in self.comprobantes.values()
            if c.cuit_contribuyente == cuit_contribuyente
            and c.condicion == condicion
            and c.fecha.month == mes
            and c.fecha.year == anio
        ]

    def registrar_emision_arca(self, comprobante_id, numero_arca, cae, cae_vencimiento):
        comprobante = self.comprobantes[comprobante_id]
        comprobante.numero_arca = numero_arca
        comprobante.cae = cae
        comprobante.cae_vencimiento = cae_vencimiento
        return comprobante


def test_emitir_rechaza_comprobante_inexistente():
    negocio = NegocioArca(cliente=FakeArcaCliente(), negocio_comprobante=FakeNegocioComprobante())

    with pytest.raises(EmisionArcaInvalida):
        negocio.emitir(CUIT, comprobante_id=999)


def test_emitir_rechaza_comprobante_de_otro_contribuyente():
    comprobante = comprobante_valido(cuit_contribuyente="20999999999")
    negocio = NegocioArca(cliente=FakeArcaCliente(), negocio_comprobante=FakeNegocioComprobante([comprobante]))

    with pytest.raises(EmisionArcaInvalida):
        negocio.emitir(CUIT, comprobante_id=comprobante.id)


def test_emitir_rechaza_una_compra():
    comprobante = comprobante_valido(condicion=CondicionComprobante.COMPRA)
    negocio = NegocioArca(cliente=FakeArcaCliente(), negocio_comprobante=FakeNegocioComprobante([comprobante]))

    with pytest.raises(EmisionArcaInvalida):
        negocio.emitir(CUIT, comprobante_id=comprobante.id)


def test_emitir_rechaza_un_comprobante_ya_emitido():
    comprobante = comprobante_valido(cae="86410988122530")
    negocio = NegocioArca(cliente=FakeArcaCliente(), negocio_comprobante=FakeNegocioComprobante([comprobante]))

    with pytest.raises(EmisionArcaInvalida):
        negocio.emitir(CUIT, comprobante_id=comprobante.id)


def test_emitir_exitoso_guarda_numero_y_cae():
    comprobante = comprobante_valido()
    cliente = FakeArcaCliente()
    negocio = NegocioArca(cliente=cliente, negocio_comprobante=FakeNegocioComprobante([comprobante]))

    resultado = negocio.emitir(CUIT, comprobante_id=comprobante.id)

    assert resultado.numero_arca == 555
    assert resultado.cae == "86410988122530"
    assert cliente.llamadas_emitir == [
        (TipoComprobante.FACTURA_B, date(2026, 3, 15), 1210.0, 1000.0, 210.0)
    ]


def test_emitir_cuando_arca_rechaza_levanta_excepcion_propia():
    comprobante = comprobante_valido()
    cliente = FakeArcaCliente(excepcion_emitir=Exception("ARCA rechazó el comprobante: dato inválido"))
    negocio = NegocioArca(cliente=cliente, negocio_comprobante=FakeNegocioComprobante([comprobante]))

    with pytest.raises(EmisionArcaRechazada):
        negocio.emitir(CUIT, comprobante_id=comprobante.id)


def test_validar_mes_sin_numero_arca_queda_pendiente():
    comprobante = comprobante_valido()
    negocio = NegocioArca(cliente=FakeArcaCliente(), negocio_comprobante=FakeNegocioComprobante([comprobante]))

    resultado = negocio.validar_mes(CUIT, mes=3, anio=2026)

    assert resultado[0]["estado"] == "pendiente"


def test_validar_mes_confirmado_cuando_arca_tiene_el_comprobante():
    comprobante = comprobante_valido(numero_arca=555, cae="86410988122530")
    cliente = FakeArcaCliente(resultados_consultar={555: {"ImpTotal": 1210.0}})
    negocio = NegocioArca(cliente=cliente, negocio_comprobante=FakeNegocioComprobante([comprobante]))

    resultado = negocio.validar_mes(CUIT, mes=3, anio=2026)

    assert resultado[0]["estado"] == "confirmado"
    assert resultado[0]["total_en_arca"] == 1210.0


def test_validar_mes_no_encontrado_cuando_arca_no_lo_tiene():
    comprobante = comprobante_valido(numero_arca=555, cae="86410988122530")
    cliente = FakeArcaCliente(resultados_consultar={})
    negocio = NegocioArca(cliente=cliente, negocio_comprobante=FakeNegocioComprobante([comprobante]))

    resultado = negocio.validar_mes(CUIT, mes=3, anio=2026)

    assert resultado[0]["estado"] == "no_encontrado_en_arca"
