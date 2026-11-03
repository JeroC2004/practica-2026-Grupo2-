from datetime import date

from business.arca_cliente import ArcaCliente, id_alicuota_iva
from business.excepciones import ArcaNoConfigurada, EmisionArcaInvalida, EmisionArcaRechazada
from business.modelos import CondicionComprobante, TipoComprobante
from business.negocio_comprobante import TOLERANCIA_REDONDEO, NegocioComprobante
from business.negocio_contribuyente import NegocioContribuyente

# ARCA acepta comprobantes de productos con fecha hasta 5 días antes o después
# de la fecha de emisión real.
DIAS_TOLERANCIA_FECHA = 5

TIPOS_EMITIBLES = (TipoComprobante.FACTURA_A, TipoComprobante.FACTURA_B, TipoComprobante.FACTURA_C)


class NegocioArca(object):

    def __init__(self, cliente=None, negocio_comprobante=None, negocio_contribuyente=None):
        self.cliente = cliente or ArcaCliente()
        self.negocio_comprobante = negocio_comprobante or NegocioComprobante()
        self.negocio_contribuyente = negocio_contribuyente
        self.hoy = date.today

    def _condicion_iva_de(self, cuit):
        """Condición frente al IVA de un CUIT si está registrado en el sistema, o None."""
        if self.negocio_contribuyente is None:
            self.negocio_contribuyente = NegocioContribuyente()
        contribuyente = self.negocio_contribuyente.obtener(cuit)
        return contribuyente.condicion_iva if contribuyente else None

    def emitir(self, cuit_contribuyente, comprobante_id):
        """
        Emite en ARCA (homologación) un comprobante de venta ya cargado, y le
        guarda el número oficial y el CAE.
        :rtype: Comprobante
        :raise: EmisionArcaInvalida, EmisionArcaRechazada, ArcaNoConfigurada
        """
        comprobante = self.negocio_comprobante.obtener(comprobante_id)
        self.regla_comprobante_existe(comprobante)
        self.regla_pertenece_al_contribuyente(comprobante, cuit_contribuyente)
        self.regla_es_venta(comprobante)
        self.regla_no_emitido(comprobante)
        self.regla_tipo_emitible(comprobante)
        self.regla_fecha_emitible(comprobante)
        self.regla_iva_emitible(comprobante)

        condicion_receptor = (
            self._condicion_iva_de(comprobante.cuit_contraparte)
            if comprobante.tipo == TipoComprobante.FACTURA_A
            else None
        )
        try:
            resultado = self.cliente.emitir(comprobante, condicion_receptor)
        except ArcaNoConfigurada:
            raise
        except Exception as error:
            raise EmisionArcaRechazada(str(error)) from error

        return self.negocio_comprobante.registrar_emision_arca(
            comprobante_id, resultado["numero_arca"], resultado["cae"], resultado["cae_vencimiento"]
        )

    def validar_mes(self, cuit_contribuyente, mes, anio):
        """
        Compara cada venta del mes contra ARCA: las que tienen CAE se vuelven a
        consultar en vivo y se comparan campo a campo (fecha, neto, IVA, total
        y CAE); las que no tienen CAE quedan como pendientes de emitir.
        :rtype: list[dict]
        """
        ventas = self.negocio_comprobante.listar_por_mes(cuit_contribuyente, CondicionComprobante.VENTA, mes, anio)
        resultado = []
        for venta in ventas:
            if venta.numero_arca is None:
                resultado.append(self._item(venta, estado="pendiente", info_arca=None, diferencias=[]))
                continue
            info_arca = self.cliente.consultar(venta.tipo, venta.numero_arca)
            if info_arca is None:
                resultado.append(self._item(venta, estado="no_encontrado_en_arca", info_arca=None, diferencias=[]))
                continue
            diferencias = self.comparar(venta, info_arca)
            estado = "con_diferencias" if diferencias else "confirmado"
            resultado.append(self._item(venta, estado=estado, info_arca=info_arca, diferencias=diferencias))
        return resultado

    def validar_compras_mes(self, cuit_contribuyente, mes, anio):
        """
        Concilia en las dos direcciones las compras cargadas del mes contra las
        facturas que los proveedores le emitieron en ARCA a este CUIT:
        - confirmado / con_diferencias: está en los dos lados.
        - falta_cargar: el proveedor la emitió y no está en el libro.
        - no_encontrado_en_arca: está en el libro pero nadie la emitió.

        ARCA no tiene un servicio para listar comprobantes recibidos (eso es
        "Mis Comprobantes", solo web con clave fiscal), así que las recibidas
        se toman de las ventas emitidas a este CUIT por otros usuarios del
        sistema, y cada una se confirma en vivo contra ARCA.
        :rtype: list[dict]
        """
        compras = self.negocio_comprobante.listar_por_mes(cuit_contribuyente, CondicionComprobante.COMPRA, mes, anio)
        recibidas = self.negocio_comprobante.listar_ventas_emitidas_a(cuit_contribuyente, mes, anio)

        sin_conciliar = {self._clave_compra(c.cuit_contraparte, c): c for c in compras}
        resultado = []
        for recibida in recibidas:
            info_arca = self.cliente.consultar(recibida.tipo, recibida.numero_arca)
            if info_arca is None or info_arca["doc_receptor"] not in ("", cuit_contribuyente):
                continue
            compra = sin_conciliar.pop(self._clave_compra(recibida.cuit_contribuyente, recibida), None)
            if compra is None:
                resultado.append(self._item_compra(recibida, recibida.cuit_contribuyente, "falta_cargar", info_arca, []))
                continue
            diferencias = self.comparar(compra, info_arca, incluir_cae=False)
            estado = "con_diferencias" if diferencias else "confirmado"
            resultado.append(self._item_compra(compra, compra.cuit_contraparte, estado, info_arca, diferencias))

        for compra in sin_conciliar.values():
            resultado.append(self._item_compra(compra, compra.cuit_contraparte, "no_encontrado_en_arca", None, []))
        return sorted(resultado, key=lambda item: (item["cuit_emisor"], item["punto_venta"], item["numero"]))

    @staticmethod
    def _clave_compra(cuit_emisor, comprobante):
        """Una factura se identifica por emisor + tipo + punto de venta + número."""
        return (cuit_emisor, comprobante.tipo, comprobante.punto_venta, comprobante.numero)

    @staticmethod
    def _item_compra(comprobante, cuit_emisor, estado, info_arca, diferencias):
        cargada = estado != "falta_cargar"
        return {
            "comprobante_id": comprobante.id if cargada else None,
            "cuit_emisor": cuit_emisor,
            "tipo": comprobante.tipo,
            "punto_venta": comprobante.punto_venta,
            "numero": comprobante.numero,
            "fecha": comprobante.fecha,
            "total": comprobante.total if cargada else None,
            "estado": estado,
            "cae": info_arca["cae"] if info_arca else None,
            "total_en_arca": info_arca["total"] if info_arca else None,
            "diferencias": diferencias,
        }

    @staticmethod
    def comparar(comprobante, info_arca, incluir_cae=True):
        """
        Devuelve las diferencias entre el comprobante cargado y lo que tiene
        ARCA. Los importes se comparan con tolerancia de redondeo. En las
        compras no se compara el CAE, porque no se carga en el libro.
        :rtype: list[dict] con campo, local y arca
        """
        locales = {
            "fecha": comprobante.fecha,
            "neto": round(comprobante.neto_gravado + comprobante.neto_exento, 2),
            "iva": round(comprobante.iva, 2),
            "total": round(comprobante.total, 2),
        }
        if incluir_cae:
            locales["cae"] = comprobante.cae
        diferencias = []
        for campo, local in locales.items():
            arca = info_arca[campo]
            if isinstance(arca, float):
                distintos = abs(local - arca) > TOLERANCIA_REDONDEO
                local, arca = f"{local:.2f}", f"{arca:.2f}"
            else:
                distintos = local != arca
            if distintos:
                diferencias.append({"campo": campo, "local": str(local), "arca": str(arca)})
        return diferencias

    @staticmethod
    def _item(comprobante, estado, info_arca, diferencias):
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
            "total_en_arca": info_arca["total"] if info_arca else None,
            "diferencias": diferencias,
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

    def regla_tipo_emitible(self, comprobante):
        """
        Las notas de crédito/débito necesitan informar la factura que ajustan
        (comprobante asociado), dato que el sistema no registra: solo se
        emiten facturas A, B y C.
        :raise: EmisionArcaInvalida
        :rtype: bool
        """
        if comprobante.tipo not in TIPOS_EMITIBLES:
            raise EmisionArcaInvalida("Solo se pueden emitir a ARCA facturas A, B o C.")
        return True

    def regla_fecha_emitible(self, comprobante):
        """
        ARCA rechaza comprobantes con fecha a más de 5 días de la fecha de
        emisión: se valida antes para dar un error claro.
        :raise: EmisionArcaInvalida
        :rtype: bool
        """
        dias = abs((comprobante.fecha - self.hoy()).days)
        if dias > DIAS_TOLERANCIA_FECHA:
            raise EmisionArcaInvalida(
                f"ARCA solo acepta comprobantes con fecha dentro de los {DIAS_TOLERANCIA_FECHA} días "
                f"de hoy ({self.hoy():%d/%m/%Y}); este tiene fecha {comprobante.fecha:%d/%m/%Y}."
            )
        return True

    def regla_iva_emitible(self, comprobante):
        """
        La factura C no discrimina IVA. En A y B, el IVA tiene que
        corresponder a una alícuota vigente sobre el neto gravado.
        :raise: EmisionArcaInvalida
        :rtype: bool
        """
        if comprobante.tipo == TipoComprobante.FACTURA_C:
            if comprobante.iva > 0:
                raise EmisionArcaInvalida("La factura C no discrimina IVA: el IVA debe ser 0.")
            return True
        if comprobante.neto_gravado > 0 and id_alicuota_iva(comprobante.neto_gravado, comprobante.iva) is None:
            raise EmisionArcaInvalida(
                "El IVA no corresponde a ninguna alícuota vigente (0%, 2,5%, 5%, 10,5%, 21% o 27%) sobre el neto gravado."
            )
        return True
