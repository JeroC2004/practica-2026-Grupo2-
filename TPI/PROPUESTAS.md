# Propuestas de Proyecto - TPI


## Propuesta 1: Gestor de Gastos Personales y Grupales con Reconocimiento de Comprobantes

### Descripción del proyecto

Aplicación web que permite a un usuario fotografiar sus facturas, tickets o comprobantes de gasto (factura de luz, ticket de supermercado, restaurante, etc.), reconocer automáticamente el tipo de gasto mediante visión por computadora y OCR, y llevar un registro histórico mes a mes. Adicionalmente, permite crear grupos con otros usuarios para dividir gastos compartidos (de forma manual o a partir de un comprobante fotografiado), generando deudas individuales entre los integrantes que pueden saldarse mediante un link de pago de Mercado Pago.

### Cálculo complejo: simplificación de deudas grupales

Cuando un grupo acumula muchas deudas cruzadas (A le debe a B, B le debe a C, C le debe a A), el sistema no pide un pago por cada deuda suelta, sino que calcula el **mínimo número de transacciones** para saldar todo el grupo:

1. Calcular el saldo neto de cada integrante (lo que le deben − lo que debe).
2. Separar a los integrantes en deudores (saldo negativo) y acreedores (saldo positivo).
3. Emparejar de a uno al mayor deudor con el mayor acreedor, saldar el menor de los dos montos, y repetir hasta que todos los saldos queden en 0.

Es un algoritmo (no una simple resta) fácil de testear: se le pasa una lista de deudas y se verifica que los saldos finales cierren en 0 con la menor cantidad posible de pagos.

---

## Propuesta 2: Libro de IVA Digital con Reconocimiento de Comprobantes y Validación contra ARCA

### Descripción del proyecto

Aplicación web orientada a monotributistas/responsables inscriptos que permite fotografiar sus facturas de compra y venta, extraer automáticamente los datos fiscales relevantes (CUIT, tipo de comprobante, punto de venta, número, fecha, importes netos e IVA) mediante visión por computadora y OCR, y generar de forma automática el Libro de IVA Compras/Ventas mes a mes. El cierre mensual del libro se contrasta contra la información disponible en ARCA (ex AFIP) para detectar diferencias entre lo declarado por el usuario y lo registrado en el organismo.

### Cálculo complejo: prorrateo de crédito fiscal

Cuando el contribuyente tiene ventas gravadas y exentas mezcladas, no puede usar el 100% del IVA de sus compras: hay que **prorratearlo** según qué proporción de las ventas totales del período fue gravada:

```
coeficiente = ventas_gravadas / (ventas_gravadas + ventas_exentas)
credito_fiscal_computable = iva_credito_total * coeficiente
```

La complejidad extra es que ese coeficiente se recalcula de forma **acumulada** a lo largo del ejercicio fiscal (no aislado mes a mes), lo que da lugar a reglas de negocio testeables como "el coeficiente nunca puede superar 1" o "sin ventas exentas, el coeficiente es 1".

