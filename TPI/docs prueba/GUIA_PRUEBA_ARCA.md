# Guía de prueba: OCR, emisión y validación contra ARCA

Actualizada al **10/11/2026**. Preparar y ejecutar la aplicación según el [README](../README.md).

La integración usa el ambiente de **homologación** y el CUIT de desarrollo compartido de Afip SDK. No genera facturas de producción para los usuarios registrados.

## Preparación

1. Instalar Tesseract y configurar su ruta si no se detecta automáticamente.
2. Completar `ARCA_TOKEN` y `JWT_SECRET` en `TPI/.env`. `ARCA_PUNTO_VENTA` vacío usa 4242.
3. Iniciar backend y frontend. Registrar los usuarios de la tabla con una contraseña y su confirmación.

| Usuario | CUIT | Condición |
|---|---|---|
| Magali Monotributo | `20304050607` | Monotributo |
| Distribuidora del Litoral SRL | `30712345673` | Responsable inscripto |

## Imágenes disponibles

| Archivo | Uso |
|---|---|
| `factura_prueba_A.png` | Reconocimiento de una factura A |
| `factura_prueba_B.png` | Reconocimiento de una factura B |
| `compras/factura_A_litoral_a_magui_20261110.png` | Operación de Litoral a Magali |
| `compras/factura_C_magui_a_litoral_20261110.png` | Operación de Magali a Litoral |

El OCR propone compra o venta según el emisor y el CUIT de la sesión. Revisar tipo, contraparte, punto de venta, número, fecha e importes antes de guardar. Para emitir, usar una fecha dentro de cinco días respecto de hoy. En ambos lados de una operación, mantener la misma fecha.

## Emitir y validar una venta

1. Iniciar sesión con el emisor de la imagen seleccionada.
2. Abrir Cargar comprobante, seleccionar la imagen y pulsar Completar con OCR.
3. Revisar los datos. Para factura C, el IVA debe ser cero; el total debe coincidir con la suma de los importes.
4. Guardar y abrir el Libro de IVA del período.
5. Pulsar Emitir en ARCA en la venta y esperar la confirmación. Se guardan número ARCA, CAE y vencimiento.
6. Abrir Validar con ARCA y consultar el mismo período. La venta emitida debe coincidir si no se modificaron sus datos.

Las ventas sin emisión figuran pendientes. Las notas de crédito y débito se pueden registrar, pero no emitir desde la aplicación.

## Conciliar compras

Para probar una compra de Magali, usar la factura A de Litoral a Magali:

1. Como Litoral, cargarla como venta y emitirla.
2. Cerrar sesión e ingresar como Magali.
3. Cargar la misma imagen como compra, manteniendo tipo, punto de venta, número, fecha e importes.
4. Consultar Validar con ARCA, sección Compras. Debe figurar Coincide con ARCA.

Se puede repetir el circuito inverso con la factura C de Magali a Litoral, cambiando los usuarios.

La conciliación identifica la operación por emisor, tipo, punto de venta y número local. El número oficial asignado por ARCA se almacena por separado.

### Variantes para observar cada estado

Usar operaciones distintas para cada variante: la aplicación no expone edición ni eliminación, y rechaza duplicados.

| Escenario | Preparación | Resultado esperado |
|---|---|---|
| Coincidencia | Emisor emite; receptor carga los mismos datos | Coincide con ARCA |
| Diferencia | Emisor emite; receptor carga importes diferentes manteniendo total = netos + IVA | Con diferencias |
| Compra faltante | Emisor emite; receptor no la carga | Falta cargar |
| Sin emisión encontrada | Receptor carga; emisor no emite | No está en ARCA |

Las compras recibidas se obtienen de las ventas emitidas por otros usuarios de este sistema y se consultan en vivo individualmente. Este circuito no permite consultar todas las compras externas de un CUIT desde Mis Comprobantes.

## Estadísticas y Libro de IVA

1. Registrar compras y ventas en varios períodos, o ejecutar el [cargador de datos ficticios](../README.md#datos-ficticios-y-pruebas) para un CUIT registrado.
2. Consultar Estadísticas por año y luego por mes. Verificar totales con IVA, cantidades y detalle mensual.
3. Comprobar que las notas de crédito se restan en estadísticas y siguen contando como comprobantes.
4. Entrar al libro usando Ver comprobantes y confirmar el período.
5. Para probar el prorrateo, registrar ventas gravadas y exentas y comparar el coeficiente con los acumulados desde enero.

El libro y el prorrateo aún no invierten el signo de las notas de crédito como lo hacen las estadísticas; es un pendiente documentado en el [proyecto](../PROYECTO.md#límites-y-pendientes).

## Problemas comunes

- **OCR no disponible:** verificar la instalación del ejecutable de Tesseract y `TESSERACT_CMD`.
- **Datos incompletos o incorrectos:** corregir el formulario antes de guardar; la imagen puede no tener calidad suficiente para reconocer todos los campos.
- **ARCA no configurada:** completar `ARCA_TOKEN` y reiniciar el backend.
- **Fecha rechazada:** usar una fecha admitida por la validación de la aplicación y mantenerla igual en compra y venta.
- **Error de numeración o fecha en homologación:** el CUIT y el punto de venta son compartidos. Revisar el mensaje del servicio y la configuración del punto de venta.
- **Sesión expirada:** iniciar sesión nuevamente; los JWT duran 60 minutos.
- **Duplicado:** usar otro comprobante; repetir el alta con la misma clave no reemplaza el anterior.
