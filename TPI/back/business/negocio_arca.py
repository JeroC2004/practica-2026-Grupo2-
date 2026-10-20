from business.arca_cliente import ArcaCliente
from business.excepciones import EmisionArcaInvalida, EmisionArcaRechazada
from business.modelos import CondicionComprobante
from business.negocio_comprobante import NegocioComprobante


class NegocioArca(object):

    def __init__(self, cliente=None, negocio_comprobante=None):
        self.cliente = cliente or ArcaCliente()
        self.negocio_comprobante = negocio_comprobante or NegocioComprobante()

    def emitir(self, cuit_contribuyente, comprobante_id):
        """
        Emite en ARCA (homologación) un comprobante de venta ya cargado, y le
        guarda el número oficial y el CAE.
        :rtype: Comprobante
        :raise: EmisionArcaInvalida, EmisionArcaRechazada
        """
        comprobante = self.negocio_comprobante.obtener(comprobante_id)
        self.regla_comprobante_existe(comprobante)
        self.regla_pertenece_al_contribuyente(comprobante, cuit_contribuyente)
        self.regla_es_venta(comprobante)
        self.regla_no_emitido(comprobante)

        try:
            resultado = self.cliente.emitir(
                comprobante.tipo, comprobante.fecha, comprobante.total, comprobante.neto_gravado, comprobante.iva
            )
        except Exception as error:
            raise EmisionArcaRechazada(str(error)) from error

        return self.negocio_comprobante.registrar_emision_arca(
            comprobante_id, resultado["numero_arca"], resultado["cae"], resultado["cae_vencimiento"]
        )

    def validar_mes(self, cuit_contribuyente, mes, anio):
        """
        Vuelve a consultar ARCA en vivo por cada venta del mes que ya tenga
        CAE, para confirmar que sigue vigente; las que no tengan CAE quedan
        como pendientes de emitir.
        :rtype: list[dict]
        """
        ventas = self.negocio_comprobante.listar_por_mes(cuit_contribuyente, CondicionComprobante.VENTA, mes, anio)
        resultado = []
        for venta in ventas:
            if venta.numero_arca is None:
                resultado.append(self._item(venta, estado="pendiente", info_arca=None))
                continue
            info_arca = self.cliente.consultar(venta.tipo, venta.numero_arca)
            estado = "confirmado" if info_arca else "no_encontrado_en_arca"
            resultado.append(self._item(venta, estado=estado, info_arca=info_arca))
        return resultado

    @staticmethod
    def _item(comprobante, estado, info_arca):
        return {
            "comprobante_id": comprobante.id,
            "tipo": comprobante.tipo,
            "punto_venta": comprobante.punto_venta,
            "numero": comprobante.numero,
            "numero_arca": comprobante.numero_arca,
            "fecha": comprobante.fecha,
            "total": comprobante.total,
            "estado": estado,
            "cae": comprobante.cae,
            "cae_vencimiento": comprobante.cae_vencimiento,
            "total_en_arca": float(info_arca["ImpTotal"]) if info_arca else None,
        }

    def regla_comprobante_existe(self, comprobante):
        """
        :raise: EmisionArcaInvalida
        :rtype: bool
        """
        if comprobante is None:
            raise EmisionArcaInvalida("El comprobante no existe.")
        return True

    def regla_pertenece_al_contribuyente(self, comprobante, cuit_contribuyente):
        """
        :raise: EmisionArcaInvalida
        :rtype: bool
        """
        if comprobante.cuit_contribuyente != cuit_contribuyente:
            raise EmisionArcaInvalida("El comprobante no pertenece a este contribuyente.")
        return True

    def regla_es_venta(self, comprobante):
        """
        Solo las ventas se emiten a ARCA: las compras ya vienen con el CAE de
        quien las emitió (tu proveedor), no es algo que vos emitas.
        :raise: EmisionArcaInvalida
        :rtype: bool
        """
        if comprobante.condicion != CondicionComprobante.VENTA:
            raise EmisionArcaInvalida("Solo se pueden emitir a ARCA los comprobantes de venta.")
        return True

    def regla_no_emitido(self, comprobante):
        """
        :raise: EmisionArcaInvalida
        :rtype: bool
        """
        if comprobante.cae:
            raise EmisionArcaInvalida("Este comprobante ya fue emitido en ARCA.")
        return True
