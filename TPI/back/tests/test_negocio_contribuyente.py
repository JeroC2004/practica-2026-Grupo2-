import pytest

from business.excepciones import CuitInvalido, CuitDuplicado, CredencialesInvalidas
from business.modelos import CondicionIva, Contribuyente
from business.negocio_contribuyente import NegocioContribuyente, _hashear_password


class FakeDatosContribuyente:
    def __init__(self, existentes=None):
        self.existentes = existentes or {}

    def existe_cuit(self, cuit):
        return cuit in self.existentes

    def buscar_por_cuit(self, cuit):
        return self.existentes.get(cuit)

    def alta(self, contribuyente):
        self.existentes[contribuyente.cuit] = contribuyente
        return contribuyente


def test_registrar_con_cuit_invalido_levanta_excepcion():
    negocio = NegocioContribuyente()
    negocio.datos = FakeDatosContribuyente()

    with pytest.raises(CuitInvalido):
        negocio.registrar("no-es-un-cuit", "Juan Perez", CondicionIva.MONOTRIBUTO, "secreta")


def test_registrar_con_cuit_duplicado_levanta_excepcion():
    negocio = NegocioContribuyente()
    negocio.datos = FakeDatosContribuyente(existentes={"20304050607": Contribuyente(
        cuit="20304050607", razon_social="Existente", condicion_iva=CondicionIva.MONOTRIBUTO,
    )})

    with pytest.raises(CuitDuplicado):
        negocio.registrar("20304050607", "Juan Perez", CondicionIva.MONOTRIBUTO, "secreta")


def test_login_con_password_correcta():
    negocio = NegocioContribuyente()
    negocio.datos = FakeDatosContribuyente()
    registrado = negocio.registrar("20304050607", "Juan Perez", CondicionIva.MONOTRIBUTO, "secreta")

    logueado = negocio.login("20304050607", "secreta")

    assert logueado.cuit == registrado.cuit


def test_login_con_password_incorrecta_levanta_excepcion():
    negocio = NegocioContribuyente()
    negocio.datos = FakeDatosContribuyente()
    negocio.registrar("20304050607", "Juan Perez", CondicionIva.MONOTRIBUTO, "secreta")

    with pytest.raises(CredencialesInvalidas):
        negocio.login("20304050607", "incorrecta")


def test_el_password_nunca_se_guarda_en_texto_plano():
    hash_resultante = _hashear_password("secreta")

    assert "secreta" not in hash_resultante
    assert "$" in hash_resultante
