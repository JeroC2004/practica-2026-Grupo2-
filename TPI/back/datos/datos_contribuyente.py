from business.modelos import Contribuyente, CondicionIva
from datos.db import ContribuyenteORM, crear_esquema, obtener_sesion


def _a_dominio(orm: ContribuyenteORM) -> Contribuyente:
    return Contribuyente(
        id=orm.id,
        cuit=orm.cuit,
        razon_social=orm.razon_social,
        condicion_iva=CondicionIva(orm.condicion_iva),
        password_hash=orm.password_hash,
    )


class DatosContribuyente:

    def __init__(self):
        crear_esquema()

    def existe_cuit(self, cuit):
        """
        Indica si ya existe un contribuyente registrado con ese CUIT.
        :rtype: bool
        """
        with obtener_sesion() as sesion:
            return sesion.query(ContribuyenteORM).filter_by(cuit=cuit).first() is not None

    def buscar_por_cuit(self, cuit):
        """
        Devuelve el contribuyente con ese CUIT, o None si no existe.
        :rtype: Contribuyente
        """
        with obtener_sesion() as sesion:
            orm = sesion.query(ContribuyenteORM).filter_by(cuit=cuit).first()
            return _a_dominio(orm) if orm else None

    def alta(self, contribuyente):
        """
        Da de alta un contribuyente ya validado por la capa de negocio.
        :type contribuyente: Contribuyente
        :rtype: Contribuyente
        """
        with obtener_sesion() as sesion:
            orm = ContribuyenteORM(
                cuit=contribuyente.cuit,
                razon_social=contribuyente.razon_social,
                condicion_iva=contribuyente.condicion_iva.value,
                password_hash=contribuyente.password_hash,
            )
            sesion.add(orm)
            sesion.flush()
            return _a_dominio(orm)
