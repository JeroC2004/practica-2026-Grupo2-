"""Carga comprobantes ficticios: python cargar_datos_prueba.py --cuit CUIT.

Usa el punto de venta 9999. Se puede repetir sin duplicar comprobantes.
No emite comprobantes ni consulta ARCA.
"""
import argparse
from datetime import date

from business.excepciones import ComprobanteDuplicado
from business.modelos import Comprobante, CondicionComprobante, TipoComprobante
from business.negocio_comprobante import NegocioComprobante
from datos.db import ContribuyenteORM, crear_esquema, obtener_sesion


def cargar(cuit):
    crear_esquema()
    with obtener_sesion() as sesion:
        if not sesion.query(ContribuyenteORM).filter_by(cuit=cuit).first():
            raise ValueError("El CUIT debe pertenecer a un usuario registrado.")

    negocio = NegocioComprobante()
    creados = 0
    periodos = [(2025, 11), (2025, 12)] + [(2026, mes) for mes in range(1, 12)]
    for anio, mes in periodos:
        for condicion in CondicionComprobante:
            venta = condicion == CondicionComprobante.VENTA
            neto = (85000 + mes * 12500) if venta else (40000 + mes * 6500)
            iva = round(neto * 0.21, 2)
            comprobante = Comprobante(
                cuit_contribuyente=cuit, tipo=TipoComprobante.FACTURA_A,
                punto_venta=9999, numero=anio * 100 + mes,
                fecha=date(anio, mes, 15 if venta else 8),
                cuit_contraparte="30712345673", neto_gravado=neto,
                neto_exento=0, iva=iva, total=neto + iva, condicion=condicion,
            )
            try:
                negocio.alta(comprobante)
                creados += 1
            except ComprobanteDuplicado:
                pass

    for condicion, neto in [(CondicionComprobante.VENTA, 10000), (CondicionComprobante.COMPRA, 5000)]:
        try:
            negocio.alta(Comprobante(
                cuit_contribuyente=cuit, tipo=TipoComprobante.NOTA_CREDITO,
                punto_venta=9999, numero=202611, fecha=date(2026, 11, 20),
                cuit_contraparte="30712345673", neto_gravado=neto,
                neto_exento=0, iva=neto * 0.21, total=neto * 1.21,
                condicion=condicion,
            ))
            creados += 1
        except ComprobanteDuplicado:
            pass
    print(f"Creados {creados} comprobantes de prueba para {cuit} (punto de venta 9999).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cuit", required=True)
    cargar(parser.parse_args().cuit)
