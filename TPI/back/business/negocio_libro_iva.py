from business.excepciones import CoeficienteInvalido
from business.modelos import CondicionComprobante, ResultadoLibroIva
from datos.datos_libro_iva import DatosLibroIva


class NegocioLibroIva(object):

    def __init__(self, datos=None, negocio_comprobante=None):
        self.datos = datos or DatosLibroIva()
        if negocio_comprobante is None:
            from business.negocio_comprobante import NegocioComprobante
            negocio_comprobante = NegocioComprobante()
        self.negocio_comprobante = negocio_comprobante

    def calcular_coeficiente_prorrateo(self, cuit_contribuyente, anio, hasta_mes):
        """
        Calcula el coeficiente de prorrateo de crédito fiscal, acumulando las
        ventas gravadas y exentas desde el inicio del ejercicio fiscal (no mes
        aislado) hasta el mes indicado.

        coeficiente = ventas_gravadas_acumuladas / (ventas_gravadas_acumuladas + ventas_exentas_acumuladas)

        Reglas de negocio:
        - Si no hubo ventas exentas (o no hubo ventas en absoluto), el coeficiente es 1.
        - El coeficiente nunca puede ser mayor a 1 ni negativo.

        :rtype: float
        :raise: CoeficienteInvalido
        """
        ventas_gravadas, ventas_exentas = self.datos.totales_ventas_acumuladas(
            cuit_contribuyente, anio, hasta_mes
        )

        if ventas_exentas == 0:
            return 1.0

        coeficiente = ventas_gravadas / (ventas_gravadas + ventas_exentas)

        if coeficiente < 0 or coeficiente > 1:
            raise CoeficienteInvalido(
                f"El coeficiente de prorrateo calculado ({coeficiente}) está fuera del rango [0, 1]."
            )

        return round(coeficiente, 4)

    def calcular_credito_fiscal_computable(self, cuit_contribuyente, mes, anio):
        """
        Calcula el crédito fiscal de IVA que puede computarse en un mes, aplicando
        el coeficiente de prorrateo acumulado del ejercicio sobre el IVA crédito
        de las compras de ese mes.

        credito_computable = iva_credito_compras_del_mes * coeficiente_prorrateo_acumulado

        :rtype: float
        """
        coeficiente = self.calcular_coeficiente_prorrateo(cuit_contribuyente, anio, hasta_mes=mes)
        iva_compras_mes = self.datos.total_iva_compras_mes(cuit_contribuyente, mes, anio)
        return round(iva_compras_mes * coeficiente, 2)

    def armar_libro_iva(self, cuit_contribuyente, mes, anio):
        """
        Arma el Libro de IVA (compras y ventas) de un mes, junto con el coeficiente
        de prorrateo y el crédito fiscal computable de ese período.
        :rtype: ResultadoLibroIva
        """
        compras = self.negocio_comprobante.listar_por_mes(
            cuit_contribuyente, CondicionComprobante.COMPRA, mes, anio
        )
        ventas = self.negocio_comprobante.listar_por_mes(
            cuit_contribuyente, CondicionComprobante.VENTA, mes, anio
        )
        return ResultadoLibroIva(
            cuit_contribuyente=cuit_contribuyente,
            mes=mes,
            anio=anio,
            compras=compras,
            ventas=ventas,
            coeficiente_prorrateo=self.calcular_coeficiente_prorrateo(cuit_contribuyente, anio, hasta_mes=mes),
            credito_fiscal_computable=self.calcular_credito_fiscal_computable(cuit_contribuyente, mes, anio),
        )
