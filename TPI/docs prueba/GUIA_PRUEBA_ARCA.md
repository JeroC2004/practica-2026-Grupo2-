# Guía de prueba: OCR, emisión y validación contra ARCA

Esta guía recorre de punta a punta las funciones de ARCA del Libro de IVA:
cargar comprobantes con OCR, emitir ventas en ARCA y validar ventas y compras
contra lo que ARCA tiene registrado.

Todo corre contra el **ambiente de homologación** (de prueba) de ARCA, usando
el CUIT de desarrollo compartido de Afip SDK. No se emite nada real.

## Documentos de prueba

| Archivo | Qué es | Para qué sirve |
|---|---|---|
| `factura_prueba_A.png` | Factura A de *Juan Perez Servicios* | Probar el OCR de una venta |
| `factura_prueba_B.png` | Factura B de *Juan Perez Servicios* | Probar el OCR y la emisión de una venta |
| `compras/compra_1_coincide.png` | Factura A N° 0003-00000101 del proveedor | Caso **Coincide con ARCA** |
| `compras/compra_2_con_diferencias.png` | Factura A N° 0003-00000102 del proveedor | Caso **Con diferencias** |
| `compras/compra_3_falta_cargar.png` | Factura A N° 0003-00000103 del proveedor | Caso **Falta cargar** |
| `compras/compra_4_no_esta_en_arca.png` | Factura A N° 0003-00000104 del proveedor | Caso **No está en ARCA** |

Las cuatro facturas de `compras/` las emite **Distribuidora del Litoral SRL**
(CUIT `30712345673`) a **Magali Monotributo** (CUIT `20304050607`), con
fecha 03/11/2026.

## Usuarios de prueba

| Usuario | CUIT | Condición frente al IVA | Rol |
|---|---|---|---|
| Magali Monotributo | `20304050607` | Monotributo | Cliente: vende (factura B) y compra |
| Distribuidora del Litoral SRL | `30712345673` | Responsable Inscripto | Proveedor de Magali |

Al subir una foto, el OCR decide si es **venta** o **compra** según quién esté
logueado: si el emisor de la factura es el usuario logueado, es una venta; si
no, es una compra.

---

## 1. Preparar el entorno (una sola vez)

1. **Tesseract OCR**: instalarlo en Windows desde cualquier terminal:
   ```powershell
   winget install UB-Mannheim.TesseractOCR
   ```
   Dejar la carpeta por defecto (`C:\Program Files\Tesseract-OCR`).

2. **Token de ARCA**: crear una cuenta gratuita en <https://app.afipsdk.com>
   y copiar el *access token*.

3. **Archivo `.env`**: copiar `TPI/.env.example` como `TPI/.env` y completar:
   ```
   ARCA_TOKEN=el_token_de_afipsdk
   JWT_SECRET=cualquier_texto_largo_y_aleatorio
   ARCA_PUNTO_VENTA=
   ```
   `ARCA_PUNTO_VENTA` se puede dejar vacío (usa el 4242). Ver
   [Problemas comunes](#problemas-comunes) para cuándo cambiarlo.

4. **Dependencias**:
   ```powershell
   cd TPI\back
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt

   cd ..\front
   npm install
   ```

## 2. Levantar el sistema

Dos terminales:

```powershell
# Terminal 1 — backend (puerto 8001)
cd TPI\back
.venv\Scripts\Activate.ps1
python app.py
```

```powershell
# Terminal 2 — frontend
cd TPI\front
npm run dev
```

Abrir <http://localhost:5173>.

## 3. Registrar los dos usuarios

Desde la pantalla de registro, crear los dos usuarios de la tabla de arriba
(CUIT, razón social, condición frente al IVA y una contraseña).

> Si `20304050607` ya está registrado, alcanza con crear el del proveedor.

---

## 4. Prueba de ventas: emitir y validar

Logueado como **Magali (`20304050607`)**:

1. **Cargar comprobante** → elegir `factura_prueba_B.png` → **Completar con OCR**.
   Debe detectar: tipo **B**, condición **venta**, PV 1, N° 50, contraparte
   `30111222334`, neto 1.000, IVA 210, total 1.210.
2. **Cambiar la fecha a la de hoy.** ARCA solo acepta emitir comprobantes con
   fecha a ±5 días de la fecha real.
3. **Guardar**. Lleva al Libro de IVA del mes.
4. En la fila de la venta, **Emitir en ARCA**. Pasa a **Emitido**; pasando el
   mouse se ve el CAE que devolvió ARCA.
5. Ir a **Validar con ARCA** → sección **Ventas**: debe figurar
   **Coincide con ARCA**.

**Opcional: provocar una diferencia.** Con el venv activado, en `TPI\back`:
```powershell
python -c "import sqlite3; c=sqlite3.connect('tpi.db'); c.execute('update comprobantes set total = total + 100 where cae is not null'); c.commit()"
```
Recargar **Validar con ARCA**: la venta pasa a **Con diferencias** con
`Total: local 1310.00 · ARCA 1210.00`. Para revertir, repetir con `total - 100`.

---

## 5. Prueba de compras: conciliación en las dos direcciones

ARCA no tiene un servicio web para listar las facturas *recibidas* (eso es
"Mis Comprobantes", que solo existe en la web con clave fiscal). Por eso, en la
prueba, el proveedor es otro usuario del sistema: sus ventas emitidas en ARCA a
tu CUIT son tus facturas recibidas, y cada una se confirma en vivo contra ARCA.

> **Fecha:** las facturas tienen fecha 03/11/2026. Si la prueba se hace otro
> día, en **todas** las cargas (del proveedor y de Magali) cambiar la fecha a
> la de hoy, **la misma en ambos lados**. Si no, la emisión falla (±5 días) o la
> conciliación marca diferencia de fecha.

### 5.1 El proveedor emite sus facturas

Cerrar sesión y entrar como **Distribuidora del Litoral (`30712345673`)**.
Para cada una de estas tres facturas:

- `compras/compra_1_coincide.png`
- `compras/compra_2_con_diferencias.png`
- `compras/compra_3_falta_cargar.png`

1. **Cargar comprobante** → elegir la imagen → **Completar con OCR**.
   Debe detectar tipo **A** y condición **venta** (el proveedor es el emisor).
2. **Guardar**.
3. En el Libro de IVA, **Emitir en ARCA**. Esperar a que pase a **Emitido**
   antes de emitir la siguiente.

`compra_4_no_esta_en_arca.png` **no** se carga del lado del proveedor: es una
factura que el proveedor nunca emitió.

### 5.2 Magali carga sus compras

Cerrar sesión y entrar como **Magali (`20304050607`)**:

| Imagen | Qué hacer |
|---|---|
| `compra_1_coincide.png` | OCR → **Guardar** sin cambios |
| `compra_2_con_diferencias.png` | OCR → cambiar a neto **19000**, IVA **3990**, total **22990** → **Guardar** |
| `compra_3_falta_cargar.png` | **No cargarla** |
| `compra_4_no_esta_en_arca.png` | OCR → **Guardar** sin cambios |

En todas, el OCR debe detectar tipo **A** y condición **compra**.

### 5.3 Validar

Ir a **Validar con ARCA** → sección **Compras**. Resultado esperado:

| Comprobante | Estado | Por qué |
|---|---|---|
| A 0003-00000101 | **Coincide con ARCA** | El proveedor la emitió y la cargaste igual |
| A 0003-00000102 | **Con diferencias** | Neto, IVA y total no coinciden con ARCA |
| A 0003-00000103 | **Falta cargar** | El proveedor la emitió y no está en tu libro |
| A 0003-00000104 | **No está en ARCA** | La cargaste pero nadie la emitió |

---

## Cómo funciona por dentro

- **Emisión**: todas las emisiones salen del CUIT de desarrollo de Afip SDK
  (`20409378472`), en el punto de venta `ARCA_PUNTO_VENTA` (4242 por defecto).
  ARCA asigna su propio número (el "número ARCA") y devuelve el CAE.
- **Factura A**: identifica al receptor por CUIT. Si el receptor está
  registrado en el sistema se informa su condición frente al IVA (monotributo o
  responsable inscripto). Las facturas B y C se emiten a consumidor final.
- **Validación de ventas**: por cada venta con CAE se consulta el comprobante en
  ARCA (`FECompConsultar`) y se comparan fecha, neto, IVA, total y CAE.
- **Conciliación de compras**: las facturas recibidas son las ventas de otros
  usuarios del sistema hechas a tu CUIT y ya emitidas. Cada una se confirma en
  ARCA (que exista y que el receptor sea tu CUIT) y se busca en tus compras por
  CUIT del emisor + tipo + punto de venta + número.
- **Con ARCA real**, las facturas recibidas se obtendrían del archivo que exporta
  "Mis Comprobantes → Recibidos"; la lógica de conciliación es la misma.

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| "Tesseract OCR no está instalado" | Falta el programa de OCR | Ver paso 1.1 y reiniciar el backend |
| "Falta configurar ARCA_TOKEN" | No hay `.env` o está vacío | Ver paso 1.3 y reiniciar el backend |
| "ARCA solo acepta comprobantes con fecha dentro de los 5 días…" | La fecha del comprobante está lejos de hoy | Cambiar la fecha a la de hoy |
| "ARCA ya autorizó en el punto de venta… un comprobante con fecha…" | Alguien emitió en ese punto de venta con una fecha posterior | Usar esa fecha o cambiar `ARCA_PUNTO_VENTA` en `.env` (por ej. 2026 o 777) y reiniciar el backend |
| `(10016)` al emitir | Se mandó dos veces la misma emisión | Recargar: la primera seguramente se emitió bien |
| La página muestra 404 o no carga datos | Otro programa usa el puerto 8001 | Cerrarlo o cambiar el puerto en `back/app.py` y `front/vite.config.ts` |

> Cambiar `ARCA_PUNTO_VENTA` hace que las ventas emitidas antes en otro punto de
> venta figuren como **No encontrado en ARCA**, porque se consultan en el nuevo.
