import hashlib
import hmac
import os
import re

from business.excepciones import CuitInvalido, CuitDuplicado, CredencialesInvalidas
from business.modelos import Contribuyente
from datos.datos_contribuyente import DatosContribuyente

CUIT_REGEX = re.compile(r"^\d{11}$")


def _hashear_password(password, salt=None):
    salt = salt or os.urandom(16).hex()
    hash_ = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000)
    return f"{salt}${hash_.hex()}"


def _verificar_password(password, password_hash):
    salt, _ = password_hash.split("$")
    return hmac.compare_digest(_hashear_password(password, salt), password_hash)


class NegocioContribuyente(object):

    def __init__(self):
        self.datos = DatosContribuyente()

    def registrar(self, cuit, razon_social, condicion_iva, password):
        """
        Registra un nuevo contribuyente, validando las reglas de negocio.
        :rtype: Contribuyente
        :raise: CuitInvalido, CuitDuplicado
        """
        self.regla_cuit_valido(cuit)
        self.regla_cuit_unico(cuit)
        contribuyente = Contribuyente(
            cuit=cuit,
            razon_social=razon_social,
            condicion_iva=condicion_iva,
            password_hash=_hashear_password(password),
        )
        return self.datos.alta(contribuyente)

    def login(self, cuit, password):
        """
        Valida las credenciales de un contribuyente.
        :rtype: Contribuyente
        :raise: CredencialesInvalidas
        """
        contribuyente = self.datos.buscar_por_cuit(cuit)
        if contribuyente is None or not _verificar_password(password, contribuyente.password_hash):
            raise CredencialesInvalidas("CUIT o contraseña incorrectos.")
        return contribuyente

    def regla_cuit_valido(self, cuit):
        """
        El CUIT debe tener 11 dígitos numéricos (sin guiones).
        :raise: CuitInvalido
        :rtype: bool
        """
        if not CUIT_REGEX.match(cuit or ""):
            raise CuitInvalido(f"El CUIT '{cuit}' debe tener 11 dígitos numéricos.")
        return True

    def regla_cuit_unico(self, cuit):
        """
        No puede existir más de un contribuyente registrado con el mismo CUIT.
        :raise: CuitDuplicado
        :rtype: bool
        """
        if self.datos.existe_cuit(cuit):
            raise CuitDuplicado(f"Ya existe un contribuyente registrado con el CUIT '{cuit}'.")
        return True
