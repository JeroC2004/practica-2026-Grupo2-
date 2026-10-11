import pytest

from business.excepciones import CoeficienteInvalido
from business.negocio_libro_iva import NegocioLibroIva

CUIT = "20304050607"


class FakeDatosLibroIva:
    """Stub de la capa de datos: no toca la base de datos real."""

    def __init__(self, totales_por_periodo=None, iva_compras_por_mes=None):
        # {(anio, hasta_mes): (ventas_gravadas, ventas_exentas)}
        self.totales_por_periodo = totales_por_periodo or {}
        # {(mes, anio): iva_compras}
        self.iva_compras_por_mes = iva_compras_por_mes or {}

    def totales_ventas_acumuladas(self, cuit_contribuyente, anio, hasta_mes):
        return self.totales_por_periodo[(anio, hasta_mes)]

    def total_iva_compras_mes(self, cuit_contribuyente, mes, anio):
        return self.iva_compras_por_mes[(mes, anio)]


class FakeNegocioComprobante:
    def listar_por_mes(self, cuit_contribuyente, condicion, mes, anio):
        return []


def negocio(totales_por_periodo=None, iva_compras_por_mes=None):
    datos = FakeDatosLibroIva(totales_por_periodo, iva_compras_por_mes)
    return NegocioLibroIva(datos=datos, negocio_comprobante=FakeNegocioComprobante())


def test_sin_ventas_exentas_el_coeficiente_es_uno():
    n = negocio(totales_por_periodo={(2026, 3): (100_000.0, 0.0)})

    coeficiente = n.calcular_coeficiente_prorrateo(CUIT, 2026, hasta_mes=3)

    assert coeficiente == 1.0


def test_sin_ventas_en_absoluto_el_coeficiente_es_uno():
    n = negocio(totales_por_periodo={(2026, 1): (0.0, 0.0)})

    coeficiente = n.calcular_coeficiente_prorrateo(CUIT, 2026, hasta_mes=1)

    assert coeficiente == 1.0


def test_ventas_mixtas_calcula_coeficiente_proporcional():
    n = negocio(totales_por_periodo={(2026, 2): (75_000.0, 25_000.0)})

    coeficiente = n.calcular_coeficiente_prorrateo(CUIT, 2026, hasta_mes=2)

    assert coeficiente == 0.75


def test_coeficiente_se_acumula_entre_meses_del_ejercicio():
    # Enero: 50% gravado / 50% exento. Febrero sólo agrega ventas gravadas,
    # por lo que el acumulado a febrero debe ser más alto que el de enero.
    n = negocio(totales_por_periodo={
        (2026, 1): (10_000.0, 10_000.0),
        (2026, 2): (40_000.0, 10_000.0),
    })

    coeficiente_enero = n.calcular_coeficiente_prorrateo(CUIT, 2026, hasta_mes=1)
    coeficiente_febrero = n.calcular_coeficiente_prorrateo(CUIT, 2026, hasta_mes=2)

    assert coeficiente_enero == 0.5
    assert coeficiente_febrero == 0.8
    assert coeficiente_febrero > coeficiente_enero


def test_coeficiente_invalido_fuera_de_rango_levanta_excepcion():
    # Datos inconsistentes (ventas gravadas negativas) deben ser detectados.
    n = negocio(totales_por_periodo={(2026, 1): (-5_000.0, 10_000.0)})

    with pytest.raises(CoeficienteInvalido):
        n.calcular_coeficiente_prorrateo(CUIT, 2026, hasta_mes=1)


def test_credito_fiscal_computable_aplica_el_coeficiente_acumulado():
    n = negocio(
        totales_por_periodo={(2026, 3): (75_000.0, 25_000.0)},
        iva_compras_por_mes={(3, 2026): 1_000.0},
    )

    credito = n.calcular_credito_fiscal_computable(CUIT, mes=3, anio=2026)

    assert credito == 750.0


def test_credito_fiscal_computable_sin_exentas_toma_el_iva_completo():
    n = negocio(
        totales_por_periodo={(2026, 5): (50_000.0, 0.0)},
        iva_compras_por_mes={(5, 2026): 420.0},
    )

    credito = n.calcular_credito_fiscal_computable(CUIT, mes=5, anio=2026)

    assert credito == 420.0
