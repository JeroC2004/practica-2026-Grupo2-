

## Propuesta : Libro de IVA Digital con Reconocimiento de Comprobantes y Validación contra ARCA

### Descripción del proyecto

Aplicación web orientada a monotributistas/responsables inscriptos que permite fotografiar sus facturas de compra y venta, extraer automáticamente los datos fiscales relevantes (CUIT, tipo de comprobante, punto de venta, número, fecha, importes netos e IVA) mediante visión por computadora y OCR, y generar de forma automática el Libro de IVA Compras/Ventas mes a mes. El cierre mensual del libro se contrasta contra la información disponible en ARCA (ex AFIP) para detectar diferencias entre lo declarado por el usuario y lo registrado en el organismo.

### Cálculo complejo: prorrateo de crédito fiscal

Cuando el contribuyente tiene ventas gravadas y exentas mezcladas, no puede usar el 100% del IVA de sus compras: hay que **prorratearlo** según qué proporción de las ventas totales del período fue gravada:

```
coeficiente = ventas_gravadas / (ventas_gravadas + ventas_exentas)
credito_fiscal_computable = iva_credito_total * coeficiente
```

La complejidad extra es que ese coeficiente se recalcula de forma **acumulada** a lo largo del ejercicio fiscal (no aislado mes a mes), lo que da lugar a reglas de negocio testeables como "el coeficiente nunca puede superar 1" o "sin ventas exentas, el coeficiente es 1".

