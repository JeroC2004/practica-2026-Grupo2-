# Libro de IVA Digital — TPI Grupo 2

Aplicación web con backend Python/FastAPI y frontend React/TypeScript para cargar compras y ventas, leer facturas mediante OCR, consultar el Libro de IVA con prorrateo acumulado, emitir y validar comprobantes en ARCA homologación y consultar estadísticas.

Documentación actualizada al **10/11/2026**.

- [Proyecto: alcance, reglas, dominio, arquitectura y casos de uso](PROYECTO.md).
- [Guía de prueba OCR y ARCA](docs%20prueba/GUIA_PRUEBA_ARCA.md).
- [Checklist general](checklist_general.md) y [checklist de capas](checklist_capas.md).
- [Propuesta original](PROPUESTAS.md), conservada como antecedente.

## Requisitos

- Python compatible con las versiones fijadas en `back/requirements.txt`. El código requiere sintaxis de Python 3.10 o superior; pytest 9 requiere Python 3.10 o superior.
- Node.js y npm compatibles con Vite 6.
- Tesseract instalado como programa del sistema para usar OCR; instalar `pytesseract` por pip no reemplaza ese programa.
- Token de Afip SDK para las operaciones ARCA. La carga manual, el libro y las estadísticas no requieren ese token.

## Instalación y configuración en Windows

Desde la raíz del repositorio:

```powershell
cd TPI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r back/requirements.txt
Copy-Item .env.example .env
cd front
npm ci
```

Si ya existe `TPI/.env`, conservarlo y completar las variables necesarias. No publicar sus valores.

| Variable | Uso |
|---|---|
| `JWT_SECRET` | Clave para firmar sesiones. Si falta o está vacía, se usa una clave fija de desarrollo; configurar una propia para cualquier despliegue. |
| `ARCA_TOKEN` | Access token de Afip SDK para homologación. |
| `ARCA_PUNTO_VENTA` | Punto de venta de homologación; vacío utiliza 4242. |
| `DB_PATH` | Ruta de SQLite; por defecto `TPI/back/tpi.db`. |
| `TESSERACT_CMD` | Ruta del ejecutable si no está en PATH ni en la ubicación predeterminada de Windows. |
| `TESSERACT_LANG` | Idioma instalado para OCR; por defecto `eng`. |

`back/app.py` carga automáticamente `TPI/.env`. Para scripts y pruebas ejecutados directamente, las variables adicionales deben estar disponibles en el entorno de la terminal.

En Windows el código detecta `C:\Program Files\Tesseract-OCR\tesseract.exe`. Para otra instalación, configurar `TESSERACT_CMD`.

## Ejecutar en desarrollo

En dos terminales, desde la raíz del repositorio:

```powershell
# Terminal 1: backend
.\TPI\.venv\Scripts\Activate.ps1
cd TPI/back
python app.py
```

```powershell
# Terminal 2: frontend
cd TPI/front
npm run dev
```

Abrir `http://localhost:5173`. Vite redirige `/api` a `http://localhost:8001`. La documentación interactiva está en `http://localhost:8001/docs`.

Para servir la interfaz compilada desde el backend:

```powershell
cd TPI/front
npm run build
```

Luego iniciar o reiniciar `back/app.py` y abrir `http://localhost:8001`.

## Recorrido de uso

1. Registrar un contribuyente con CUIT de 11 dígitos, razón social, condición de IVA y contraseña confirmada.
2. Iniciar sesión y cargar un comprobante manualmente o completar sus datos con OCR. Revisar siempre los valores reconocidos.
3. Consultar el Libro de IVA por mes y año para ver compras, ventas, coeficiente acumulado y crédito fiscal computable.
4. Con ARCA configurada, emitir ventas A/B/C y consultar Validar con ARCA. Se guardan número oficial, CAE y vencimiento.
5. Consultar Estadísticas por año y mes: importes con IVA, cantidades, comparación mensual y acceso al libro del período. Las notas de crédito se restan; ventas menos compras no representa la ganancia.

La integración ARCA utiliza **homologación y un CUIT compartido de desarrollo**. La conciliación de compras alcanza las ventas emitidas por otros usuarios de esta aplicación; no importa todas las compras de un CUIT desde ARCA. Ver [límites del proyecto](PROYECTO.md#límites-y-pendientes).

## Datos ficticios y pruebas

Con el entorno activado, desde `TPI/back`:

```powershell
python cargar_datos_prueba.py --cuit 20304050607
python -m pytest -q
```

El CUIT debe estar registrado. El cargador usa el punto de venta 9999 y omite duplicados; no emite ni consulta ARCA. Genera operaciones de noviembre/diciembre de 2025 y enero a noviembre de 2026, más notas de crédito de noviembre de 2026.

Las pruebas usan una SQLite temporal y cubren contribuyentes, comprobantes, prorrateo, estadísticas, OCR, seguridad y reglas ARCA. Los dobles de prueba no sustituyen una validación manual de integración en homologación.

## Estructura

```text
TPI/
  back/
    app.py                 # Entrada de la aplicación
    business/              # Dominio, reglas, OCR e integración ARCA
    datos/                 # ORM, sesiones y repositorios
    views/                 # API, esquemas, seguridad y routers
    tests/                 # Pruebas pytest
    cargar_datos_prueba.py  # Datos ficticios para usuarios registrados
    requirements.txt
  front/
    src/                   # Páginas, componentes, sesión y cliente API
    package.json
  docs prueba/             # Imágenes y guía de validación manual
  .env.example             # Configuración sin secretos
```

## API disponible

Todas las rutas llevan el prefijo `/api`; salvo registro y login, requieren `Authorization: Bearer <token>`.

| Método | Ruta | Uso |
|---|---|---|
| POST | `/auth/registro` | Registrar contribuyente |
| POST | `/auth/login` | Obtener JWT |
| GET | `/auth/me` | Consultar perfil |
| POST | `/comprobantes/ocr` | Extraer datos de imagen |
| POST / GET | `/comprobantes` | Alta / listado por período y condición |
| POST | `/comprobantes/{id}/emitir-arca` | Emitir una venta |
| GET | `/libro-iva/{anio}/{mes}` | Consultar libro y prorrateo |
| GET | `/estadisticas/{anio}` | Consultar los doce meses del año |
| GET | `/validacion-arca/{anio}/{mes}` | Validar ventas |
| GET | `/validacion-arca/compras/{anio}/{mes}` | Conciliar compras |

Los parámetros y contratos completos están en `/docs`.
