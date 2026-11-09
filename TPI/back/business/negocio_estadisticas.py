from datetime import date
from decimal import Decimal

from business.modelos import CondicionComprobante, TipoComprobante
from datos.datos_comprobante import DatosComprobante


class NegocioEstadisticas:
    def __init__(self, datos=None):
        self.datos = datos if datos is not None else DatosComprobante()

    def consultar(self, cuit, anio):
        meses = [dict(mes=mes, compras=Decimal(0), ventas=Decimal(0),
                      cantidad_compras=0, cantidad_ventas=0) for mes in range(1, 13)]
        for condicion in CondicionComprobante:
            comprobantes = self.datos.listar_por_rango(
                cuit, condicion, date(anio, 1, 1), date(anio + 1, 1, 1)
            )
            campo = "compras" if condicion == CondicionComprobante.COMPRA else "ventas"
            for comprobante in comprobantes:
                fila = meses[comprobante.fecha.month - 1]
                signo = -1 if comprobante.tipo == TipoComprobante.NOTA_CREDITO else 1
                fila[campo] += signo * Decimal(str(comprobante.total))
                fila[f"cantidad_{campo}"] += 1
        for fila in meses:
            fila["compras"] = float(round(fila["compras"], 2))
            fila["ventas"] = float(round(fila["ventas"], 2))
        return {"anio": anio, "meses": meses}
