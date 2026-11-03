import importlib

import pytest

from views import seguridad


@pytest.mark.parametrize("clave", [None, "", "clave-configurada-para-pruebas-de-al-menos-32-caracteres"])
def test_token_con_clave_ausente_vacia_o_configurada(monkeypatch, clave):
    with monkeypatch.context() as entorno:
        if clave is None:
            entorno.delenv("JWT_SECRET", raising=False)
        else:
            entorno.setenv("JWT_SECRET", clave)
        importlib.reload(seguridad)
        token = seguridad.crear_token("20304050607")
        assert seguridad._decodificar(token) == "20304050607"
        if clave:
            assert seguridad.SECRET_KEY == clave
    importlib.reload(seguridad)
