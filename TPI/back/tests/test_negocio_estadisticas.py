from datetime import date
from types import SimpleNamespace

from business.modelos import CondicionComprobante, TipoComprobante
from business.negocio_estadisticas import NegocioEstadisticas


def test_agrupa_por_mes_resta_notas_credito_y_aisla_usuario_y_anio():
    registros = [
        ("usuario", 2026, 1, CondicionComprobante.VENTA, TipoComprobante.FACTURA_A, 100.10),
        ("usuario", 2026, 1, CondicionComprobante.VENTA, TipoComprobante.NOTA_CREDITO, 20.10),
        ("usuario", 2026, 1, CondicionComprobante.COMPRA, TipoComprobante.FACTURA_C, 50),
        ("usuario", 2026, 12, CondicionComprobante.COMPRA, TipoComprobante.NOTA_CREDITO, 10),
        ("usuario", 2026, 12, CondicionComprobante.VENTA, TipoComprobante.NOTA_DEBITO, 25),
        ("otro", 2026, 1, CondicionComprobante.VENTA, TipoComprobante.FACTURA_A, 999),
        ("usuario", 2025, 1, CondicionComprobante.VENTA, TipoComprobante.FACTURA_A, 999),
    ]

    class Datos:
        def listar_por_rango(self, cuit, condicion, desde, hasta):
            return [SimpleNamespace(fecha=date(anio, mes, 1), tipo=tipo, total=total)
                    for usuario, anio, mes, clase, tipo, total in registros
                    if usuario == cuit and clase == condicion and desde <= date(anio, mes, 1) < hasta]

    resultado = NegocioEstadisticas(Datos()).consultar("usuario", 2026)
    assert resultado["anio"] == 2026
    assert len(resultado["meses"]) == 12
    assert resultado["meses"][0] == dict(mes=1, compras=50, ventas=80,
                                         cantidad_compras=1, cantidad_ventas=2)
    assert resultado["meses"][1] == dict(mes=2, compras=0, ventas=0,
                                         cantidad_compras=0, cantidad_ventas=0)
    assert resultado["meses"][11] == dict(mes=12, compras=-10, ventas=25,
                                          cantidad_compras=1, cantidad_ventas=1)
