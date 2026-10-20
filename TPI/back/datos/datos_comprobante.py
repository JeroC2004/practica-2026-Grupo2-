from datetime import date

from business.modelos import (
    Comprobante,
    TipoComprobante,
    CondicionComprobante,
    OrigenComprobante,
)
from datos.db import ComprobanteORM, crear_esquema, obtener_sesion


def _a_dominio(orm: ComprobanteORM) -> Comprobante:
    return Comprobante(
        id=orm.id,
        cuit_contribuyente=orm.cuit_contribuyente,
        tipo=TipoComprobante(orm.tipo),
        punto_venta=orm.punto_venta,
        numero=orm.numero,
        fecha=orm.fecha,
        cuit_contraparte=orm.cuit_contraparte,
        neto_gravado=orm.neto_gravado,
        neto_exento=orm.neto_exento,
        iva=orm.iva,
        total=orm.total,
        condicion=CondicionComprobante(orm.condicion),
        origen=OrigenComprobante(orm.origen),
        numero_arca=orm.numero_arca,
        cae=orm.cae,
        cae_vencimiento=orm.cae_vencimiento,
    )


class DatosComprobante:

    def __init__(self):
        crear_esquema()

    def buscar_por_clave(self, cuit_contribuyente, tipo, punto_venta, numero, condicion):
        """
        Busca un comprobante por su clave única (tipo + punto de venta + número)
        dentro de los comprobantes de un contribuyente, para detectar duplicados.
        Devuelve None si no existe.
        :rtype: Comprobante
        """
        with obtener_sesion() as sesion:
            orm = (
                sesion.query(ComprobanteORM)
                .filter_by(
                    cuit_contribuyente=cuit_contribuyente,
                    tipo=tipo.value,
                    punto_venta=punto_venta,
                    numero=numero,
                    condicion=condicion.value,
                )
                .first()
            )
            return _a_dominio(orm) if orm else None

    def obtener_por_id(self, comprobante_id):
        """
        Busca un comprobante por su id. Devuelve None si no existe.
        :rtype: Comprobante
        """
        with obtener_sesion() as sesion:
            orm = sesion.get(ComprobanteORM, comprobante_id)
            return _a_dominio(orm) if orm else None

    def actualizar_emision_arca(self, comprobante_id, numero_arca, cae, cae_vencimiento):
        """
        Guarda el resultado de emitir un comprobante en ARCA (número oficial y CAE).
        :rtype: Comprobante
        """
        with obtener_sesion() as sesion:
            orm = sesion.get(ComprobanteORM, comprobante_id)
            orm.numero_arca = numero_arca
            orm.cae = cae
            orm.cae_vencimiento = cae_vencimiento
            sesion.flush()
            return _a_dominio(orm)

    def alta(self, comprobante):
        """
        Da de alta un comprobante ya validado por la capa de negocio.
        :type comprobante: Comprobante
        :rtype: Comprobante
        """
        with obtener_sesion() as sesion:
            orm = ComprobanteORM(
                cuit_contribuyente=comprobante.cuit_contribuyente,
                tipo=comprobante.tipo.value,
                punto_venta=comprobante.punto_venta,
                numero=comprobante.numero,
                fecha=comprobante.fecha,
                cuit_contraparte=comprobante.cuit_contraparte,
                neto_gravado=comprobante.neto_gravado,
                neto_exento=comprobante.neto_exento,
                iva=comprobante.iva,
                total=comprobante.total,
                condicion=comprobante.condicion.value,
                origen=comprobante.origen.value,
            )
            sesion.add(orm)
            sesion.flush()
            return _a_dominio(orm)

    def listar_por_mes(self, cuit_contribuyente, condicion, mes, anio):
        """
        Lista los comprobantes de un contribuyente para un mes/año y una condición
        (compra o venta) determinados.
        :rtype: list[Comprobante]
        """
        desde = date(anio, mes, 1)
        hasta = date(anio + 1, 1, 1) if mes == 12 else date(anio, mes + 1, 1)
        with obtener_sesion() as sesion:
            orms = (
                sesion.query(ComprobanteORM)
                .filter(
                    ComprobanteORM.cuit_contribuyente == cuit_contribuyente,
                    ComprobanteORM.condicion == condicion.value,
                    ComprobanteORM.fecha >= desde,
                    ComprobanteORM.fecha < hasta,
                )
                .all()
            )
            return [_a_dominio(orm) for orm in orms]

    def listar_por_rango(self, cuit_contribuyente, condicion, desde, hasta):
        """
        Lista los comprobantes de un contribuyente entre dos fechas (inclusive/exclusive)
        para una condición (compra o venta) determinada.
        :rtype: list[Comprobante]
        """
        with obtener_sesion() as sesion:
            orms = (
                sesion.query(ComprobanteORM)
                .filter(
                    ComprobanteORM.cuit_contribuyente == cuit_contribuyente,
                    ComprobanteORM.condicion == condicion.value,
                    ComprobanteORM.fecha >= desde,
                    ComprobanteORM.fecha < hasta,
                )
                .all()
            )
            return [_a_dominio(orm) for orm in orms]
