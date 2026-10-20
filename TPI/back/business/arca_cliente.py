import os
from datetime import datetime

from afip import Afip

from business.modelos import TipoComprobante

PUNTO_VENTA_HOMOLOGACION = 1
CONDICION_IVA_CONSUMIDOR_FINAL = 5
ALICUOTA_IVA_21_POR_CIENTO = 5

CUIT_DESARROLLO_AFIPSDK = 20409378472

_CODIGO_AFIP_POR_TIPO = {
    TipoComprobante.FACTURA_A: 1,
    TipoComprobante.FACTURA_B: 6,
    TipoComprobante.FACTURA_C: 11,
    TipoComprobante.NOTA_CREDITO: 8,
    TipoComprobante.NOTA_DEBITO: 7,
}


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

    def __init__(self, cuit=None, access_token=None):
        self.cuit = cuit or CUIT_DESARROLLO_AFIPSDK
        self.afip = Afip({"CUIT": self.cuit, "access_token": access_token or os.environ["ARCA_TOKEN"]})

    def _ejecutar(self, metodo, params):
        ta = self.afip.getServiceTA("wsfe")
        auth = {"Token": ta["token"], "Sign": ta["sign"], "Cuit": self.cuit}
        servicio = self.afip.ElectronicBilling
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

    def ultimo_numero(self, tipo):
        """
        Último número de comprobante autorizado por ARCA para ese tipo, en el
        punto de venta de homologación.
        :rtype: int
        """
        resultado = self._ejecutar(
            "FECompUltimoAutorizado", {"PtoVta": PUNTO_VENTA_HOMOLOGACION, "CbteTipo": _CODIGO_AFIP_POR_TIPO[tipo]}
        )
        return self._desenvolver(resultado, "FECompUltimoAutorizadoResult")["CbteNro"]

    def emitir(self, tipo, fecha, total, neto_gravado, iva):
        """
        Pide a ARCA el próximo número para este tipo de comprobante y lo emite.
        :rtype: dict con numero_arca, cae y cae_vencimiento
        :raise: Exception si ARCA rechaza el comprobante (ver "Observaciones")
        """
        numero = self.ultimo_numero(tipo) + 1
        datos = {
            "FeCAEReq": {
                "FeCabReq": {
                    "CantReg": 1,
                    "PtoVta": PUNTO_VENTA_HOMOLOGACION,
                    "CbteTipo": _CODIGO_AFIP_POR_TIPO[tipo],
                },
                "FeDetReq": {
                    "FECAEDetRequest": {
                        "Concepto": 1,
                        "DocTipo": 99,
                        "DocNro": 0,
                        "CbteDesde": numero,
                        "CbteHasta": numero,
                        "CbteFch": fecha.strftime("%Y%m%d"),
                        "ImpTotal": total,
                        "ImpTotConc": 0,
                        "ImpNeto": neto_gravado,
                        "ImpOpEx": 0,
                        "ImpIVA": iva,
                        "ImpTrib": 0,
                        "MonId": "PES",
                        "MonCotiz": 1,
                        "CondicionIVAReceptorId": CONDICION_IVA_CONSUMIDOR_FINAL,
                        "Iva": {
                            "AlicIva": {"Id": ALICUOTA_IVA_21_POR_CIENTO, "BaseImp": neto_gravado, "Importe": iva}
                        },
                    }
                },
            }
        }
        respuesta = self._desenvolver(self._ejecutar("FECAESolicitar", datos), "FECAESolicitarResult")
        detalle_respuesta = respuesta["FeDetResp"]["FECAEDetResponse"]
        detalle = detalle_respuesta[0] if isinstance(detalle_respuesta, list) else detalle_respuesta

        if detalle["Resultado"] != "A":
            observaciones = detalle.get("Observaciones", {}).get("Obs", [])
            mensajes = "; ".join(obs["Msg"] for obs in observaciones) or "motivo desconocido"
            raise Exception(f"ARCA rechazó el comprobante: {mensajes}")

        return {
            "numero_arca": numero,
            "cae": detalle["CAE"],
            "cae_vencimiento": datetime.strptime(detalle["CAEFchVto"], "%Y%m%d").date(),
        }

    def consultar(self, tipo, numero):
        """
        Consulta en ARCA un comprobante ya emitido, por tipo y número.
        :rtype: dict con los datos del comprobante, o None si no existe
        """
        try:
            resultado = self._ejecutar(
                "FECompConsultar",
                {
                    "FeCompConsReq": {
                        "CbteTipo": _CODIGO_AFIP_POR_TIPO[tipo],
                        "CbteNro": numero,
                        "PtoVta": PUNTO_VENTA_HOMOLOGACION,
                    }
                },
            )
        except Exception as error:
            if str(error).startswith("(602)"):
                return None
            raise
        return self._desenvolver(resultado, "FECompConsultarResult").get("ResultGet")
