from business.excepciones import ComprobanteDuplicado, ComprobanteInvalido
from datos.datos_comprobante import DatosComprobante

TOLERANCIA_REDONDEO = 0.01


class NegocioComprobante(object):

    def __init__(self, datos=None):
        self.datos = datos or DatosComprobante()

    def alta(self, comprobante):
        """
        Da de alta un comprobante (cargado a mano o confirmado luego de OCR).
        Se deben validar las reglas de negocio primero.
        :type comprobante: Comprobante
        :rtype: Comprobante
        :raise: ComprobanteDuplicado, ComprobanteInvalido
        """
        self.regla_sin_duplicados(comprobante)
        self.regla_importes_validos(comprobante)
        return self.datos.alta(comprobante)

    def listar_por_mes(self, cuit_contribuyente, condicion, mes, anio):
        """
        Lista los comprobantes de un contribuyente para un mes/año y condición dados.
        :rtype: list[Comprobante]
        """
        return self.datos.listar_por_mes(cuit_contribuyente, condicion, mes, anio)

    def obtener(self, comprobante_id):
        """
        Devuelve un comprobante por su id, o None si no existe.
        :rtype: Comprobante
        """
        return self.datos.obtener_por_id(comprobante_id)

    def registrar_emision_arca(self, comprobante_id, numero_arca, cae, cae_vencimiento):
        """
        Guarda en el comprobante el resultado de haberlo emitido en ARCA.
        :rtype: Comprobante
        """
        return self.datos.actualizar_emision_arca(comprobante_id, numero_arca, cae, cae_vencimiento)

    def regla_sin_duplicados(self, comprobante):
        """
        No puede cargarse dos veces el mismo comprobante (mismo tipo, punto de
        venta y número) para un mismo contribuyente y condición (compra/venta).
        :raise: ComprobanteDuplicado
        :rtype: bool
        """
        existente = self.datos.buscar_por_clave(
            comprobante.cuit_contribuyente,
            comprobante.tipo,
            comprobante.punto_venta,
            comprobante.numero,
            comprobante.condicion,
        )
        if existente is not None:
            raise ComprobanteDuplicado(
                f"El comprobante {comprobante.tipo.value} "
                f"{comprobante.punto_venta:04d}-{comprobante.numero:08d} ya fue cargado."
            )
        return True

    def regla_importes_validos(self, comprobante):
        """
        Los importes no pueden ser negativos, y el total debe ser consistente con
        la suma de neto gravado + neto exento + IVA (con tolerancia de redondeo).
        :raise: ComprobanteInvalido
        :rtype: bool
        """
        importes = (comprobante.neto_gravado, comprobante.neto_exento, comprobante.iva, comprobante.total)
        if any(importe < 0 for importe in importes):
            raise ComprobanteInvalido("Los importes de un comprobante no pueden ser negativos.")

        total_calculado = comprobante.neto_gravado + comprobante.neto_exento + comprobante.iva
        if abs(total_calculado - comprobante.total) > TOLERANCIA_REDONDEO:
            raise ComprobanteInvalido(
                "El total no coincide con la suma de neto gravado, neto exento e IVA "
                f"(esperado {total_calculado:.2f}, informado {comprobante.total:.2f})."
            )
        return True
