import os
from datetime import datetime

from afip import Afip

from business.excepciones import ArcaNoConfigurada
from business.modelos import CondicionIva, TipoComprobante

# El CUIT de desarrollo es compartido por todos los usuarios de Afip SDK, y en
# el punto de venta 1 hay comprobantes de terceros con fecha futura: ARCA no
# deja autorizar uno con fecha anterior al último (error 10016). Por eso se
# usa por defecto un punto de venta poco usado, configurable con ARCA_PUNTO_VENTA.
PUNTO_VENTA_HOMOLOGACION = 4242

DOC_TIPO_CUIT = 80
DOC_TIPO_SIN_IDENTIFICAR = 99
CONDICION_IVA_RESPONSABLE_INSCRIPTO = 1
CONDICION_IVA_CONSUMIDOR_FINAL = 5
CONDICION_IVA_MONOTRIBUTO = 6

CUIT_DESARROLLO_AFIPSDK = 20409378472

_CODIGO_AFIP_POR_TIPO = {
    TipoComprobante.FACTURA_A: 1,
    TipoComprobante.FACTURA_B: 6,
    TipoComprobante.FACTURA_C: 11,
    TipoComprobante.NOTA_CREDITO: 8,
    TipoComprobante.NOTA_DEBITO: 7,
}

# Tabla de alícuotas de IVA de ARCA (FEParamGetTiposIva): tasa -> Id.
_ID_ALICUOTA_POR_TASA = {0.0: 3, 0.025: 9, 0.05: 8, 0.105: 4, 0.21: 5, 0.27: 6}


def id_alicuota_iva(neto_gravado, iva):
    """
    Deduce el Id de alícuota de ARCA a partir del neto gravado y el IVA.
    :rtype: int, o None si la proporción no corresponde a ninguna alícuota vigente
    """
    if neto_gravado <= 0:
        return None
    for tasa, id_alicuota in _ID_ALICUOTA_POR_TASA.items():
        if abs(round(neto_gravado * tasa, 2) - iva) <= 0.01:
            return id_alicuota
    return None


class ArcaCliente:
    """
    Wrapper sobre el paquete afip.py (Afip SDK) para el servicio WSFE, usando
    el CUIT de desarrollo compartido de Afip SDK (ambiente de homologación de
    ARCA): no hace falta certificado propio, solo un access_token gratuito de
    app.afipsdk.com (ver ARCA_TOKEN en el .env).

    afip.py 1.2.0 tiene dos bugs al llamar WSFE: nunca manda el bloque "Auth"
    (Token/Sign/Cuit) que ARCA exige en cada pedido, y fuerza SOAP 1.2, que
    rompe el armado del XML en el backend de Afip SDK. Acá se arman los
    pedidos a mano con el fix en vez de usar los métodos de alto nivel
    (getLastVoucher, createVoucher) que tienen ese bug.
    """

    def __init__(self, cuit=None, access_token=None, punto_venta=None):
        self.cuit = cuit or CUIT_DESARROLLO_AFIPSDK
        self.access_token = access_token or os.environ.get("ARCA_TOKEN")
        self.punto_venta = punto_venta or int(os.environ.get("ARCA_PUNTO_VENTA") or PUNTO_VENTA_HOMOLOGACION)
        self._afip = None

    def _ejecutar(self, metodo, params):
        if not self.access_token:
            raise ArcaNoConfigurada(
                "Falta configurar ARCA_TOKEN en TPI/.env (se obtiene gratis en https://app.afipsdk.com)."
            )
        if self._afip is None:
            self._afip = Afip({"CUIT": self.cuit, "access_token": self.access_token})
        ta = self._afip.getServiceTA("wsfe")
        auth = {"Token": ta["token"], "Sign": ta["sign"], "Cuit": self.cuit}
        servicio = self._afip.ElectronicBilling
        servicio.soapv12 = False
        return servicio.executeRequest(metodo, {"Auth": auth, **params})

    @staticmethod
    def _desenvolver(resultado, clave):
        """
        El backend de Afip SDK a veces envuelve la respuesta en una clave
        "<Metodo>Result" y a veces no (inconsistente entre llamados). Si no
        está esa clave, el resultado ya viene "desenvuelto".
        """
        return resultado.get(clave, resultado)

    @staticmethod
    def _como_lista(valor):
        """ARCA devuelve un dict suelto cuando hay un solo elemento, y una lista cuando hay varios."""
        if valor is None:
            return []
        return valor if isinstance(valor, list) else [valor]

    def ultimo_numero(self, tipo):
        """
        Último número de comprobante autorizado por ARCA para ese tipo, en el
        punto de venta de homologación.
        :rtype: int
        """
        resultado = self._ejecutar(
            "FECompUltimoAutorizado", {"PtoVta": self.punto_venta, "CbteTipo": _CODIGO_AFIP_POR_TIPO[tipo]}
        )
        return self._desenvolver(resultado, "FECompUltimoAutorizadoResult")["CbteNro"]

    @staticmethod
    def _receptor(comprobante, condicion_iva_receptor=None):
        """
        La factura A exige identificar al receptor por CUIT, y que sea
        Responsable Inscripto o Monotributista; B y C se emiten a consumidor final.
        """
        if comprobante.tipo == TipoComprobante.FACTURA_A:
            es_monotributo = condicion_iva_receptor == CondicionIva.MONOTRIBUTO
            return {
                "DocTipo": DOC_TIPO_CUIT,
                "DocNro": int(comprobante.cuit_contraparte),
                "CondicionIVAReceptorId": (
                    CONDICION_IVA_MONOTRIBUTO if es_monotributo else CONDICION_IVA_RESPONSABLE_INSCRIPTO
                ),
            }
        return {
            "DocTipo": DOC_TIPO_SIN_IDENTIFICAR,
            "DocNro": 0,
            "CondicionIVAReceptorId": CONDICION_IVA_CONSUMIDOR_FINAL,
        }

    @staticmethod
    def _importes(comprobante):
        """
        La factura C (monotributo) no discrimina IVA: todo va como neto y sin
        bloque "Iva". A y B separan neto gravado, exento e IVA por alícuota.
        """
        total = round(comprobante.total, 2)
        if comprobante.tipo == TipoComprobante.FACTURA_C:
            return {"ImpTotal": total, "ImpTotConc": 0, "ImpNeto": total, "ImpOpEx": 0, "ImpIVA": 0, "ImpTrib": 0}

        neto_gravado = round(comprobante.neto_gravado, 2)
        iva = round(comprobante.iva, 2)
        importes = {
            "ImpTotal": total,
            "ImpTotConc": 0,
            "ImpNeto": neto_gravado,
            "ImpOpEx": round(comprobante.neto_exento, 2),
            "ImpIVA": iva,
            "ImpTrib": 0,
        }
        if neto_gravado > 0:
            alicuota = {"Id": id_alicuota_iva(neto_gravado, iva), "BaseImp": neto_gravado, "Importe": iva}
            importes["Iva"] = {"AlicIva": alicuota}
        return importes

    def emitir(self, comprobante, condicion_iva_receptor=None):
        """
        Pide a ARCA el próximo número para este tipo de comprobante y lo emite.
        :type comprobante: Comprobante
        :type condicion_iva_receptor: CondicionIva, si el receptor está registrado en el sistema
        :rtype: dict con numero_arca, cae y cae_vencimiento
        :raise: Exception si ARCA rechaza el comprobante (ver "Observaciones")
        """
        ultimo = self.ultimo_numero(comprobante.tipo)
        anterior = self.consultar(comprobante.tipo, ultimo) if ultimo else None
        if anterior and comprobante.fecha < anterior["fecha"]:
            raise Exception(
                f"ARCA ya autorizó en el punto de venta {self.punto_venta} un comprobante con fecha "
                f"{anterior['fecha']:%d/%m/%Y}, y no acepta uno con fecha anterior ({comprobante.fecha:%d/%m/%Y}). "
                "Usá esa fecha o una posterior, o cambiá ARCA_PUNTO_VENTA en el .env."
            )
        numero = ultimo + 1
        datos = {
            "FeCAEReq": {
                "FeCabReq": {
                    "CantReg": 1,
                    "PtoVta": self.punto_venta,
                    "CbteTipo": _CODIGO_AFIP_POR_TIPO[comprobante.tipo],
                },
                "FeDetReq": {
                    "FECAEDetRequest": {
                        "Concepto": 1,
                        **self._receptor(comprobante, condicion_iva_receptor),
                        "CbteDesde": numero,
                        "CbteHasta": numero,
                        "CbteFch": comprobante.fecha.strftime("%Y%m%d"),
                        **self._importes(comprobante),
                        "MonId": "PES",
                        "MonCotiz": 1,
                    }
                },
            }
        }
        respuesta = self._desenvolver(self._ejecutar("FECAESolicitar", datos), "FECAESolicitarResult")
        detalle = self._como_lista(respuesta["FeDetResp"]["FECAEDetResponse"])[0]

        if detalle["Resultado"] != "A":
            observaciones = self._como_lista((detalle.get("Observaciones") or {}).get("Obs"))
            errores = self._como_lista((respuesta.get("Errors") or {}).get("Err"))
            mensajes = "; ".join(f"({item['Code']}) {item['Msg']}" for item in observaciones + errores)
            raise Exception(f"ARCA rechazó el comprobante: {mensajes or 'motivo desconocido'}")

        return {
            "numero_arca": numero,
            "cae": detalle["CAE"],
            "cae_vencimiento": datetime.strptime(detalle["CAEFchVto"], "%Y%m%d").date(),
        }

    def consultar(self, tipo, numero):
        """
        Consulta en ARCA un comprobante ya emitido, por tipo y número.
        :rtype: dict con fecha, neto (gravado + exento), iva, total, cae y doc_receptor, o None si no existe
        """
        try:
            resultado = self._ejecutar(
                "FECompConsultar",
                {
                    "FeCompConsReq": {
                        "CbteTipo": _CODIGO_AFIP_POR_TIPO[tipo],
                        "CbteNro": numero,
                        "PtoVta": self.punto_venta,
                    }
                },
            )
        except Exception as error:
            if str(error).startswith("(602)"):
                return None
            raise
        comprobante = self._desenvolver(resultado, "FECompConsultarResult").get("ResultGet")
        if not comprobante:
            return None
        return {
            "fecha": datetime.strptime(str(comprobante["CbteFch"]), "%Y%m%d").date(),
            "neto": float(comprobante["ImpNeto"]) + float(comprobante.get("ImpOpEx") or 0),
            "iva": float(comprobante["ImpIVA"]),
            "total": float(comprobante["ImpTotal"]),
            "cae": str(comprobante["CodAutorizacion"]),
            "doc_receptor": str(comprobante.get("DocNro") or ""),
        }
