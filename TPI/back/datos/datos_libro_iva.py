from datetime import date

from business.modelos import CondicionComprobante
from datos.datos_comprobante import DatosComprobante


class DatosLibroIva:
    """
    Agrega consultas sobre comprobantes orientadas a armar el Libro de IVA y
    calcular el prorrateo de crédito fiscal. Reutiliza DatosComprobante en vez
    de consultar la base de datos directamente.
    """

    def __init__(self, datos_comprobante=None):
        self.datos_comprobante = datos_comprobante or DatosComprobante()

    def totales_ventas_acumuladas(self, cuit_contribuyente, anio, hasta_mes):
        """
        Suma las ventas gravadas y exentas del contribuyente desde el inicio del
        ejercicio fiscal (1/1 del año) hasta el fin del mes indicado (inclusive).
        :rtype: tuple[float, float]
        """
        desde = date(anio, 1, 1)
        hasta = date(anio + 1, 1, 1) if hasta_mes == 12 else date(anio, hasta_mes + 1, 1)
        ventas = self.datos_comprobante.listar_por_rango(
            cuit_contribuyente, CondicionComprobante.VENTA, desde, hasta
        )
        ventas_gravadas = sum(v.neto_gravado for v in ventas)
        ventas_exentas = sum(v.neto_exento for v in ventas)
        return ventas_gravadas, ventas_exentas

    def total_iva_compras_mes(self, cuit_contribuyente, mes, anio):
        """
        Suma el IVA crédito de las compras del contribuyente en un mes/año puntual.
        :rtype: float
        """
        compras = self.datos_comprobante.listar_por_mes(
            cuit_contribuyente, CondicionComprobante.COMPRA, mes, anio
        )
        return sum(c.iva for c in compras)
