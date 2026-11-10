# Checklist Sobre Buenas Prácticas Desarrollando en Python

El siguiente checklist permite una fácil detección de malas prácticas y posibles correcciones.

## General

- [ ] Se respecta la convención de nombres típica de Python (PascalCase para clases, snake_case en todo lo demás).
- [ ] **No** se utilizan variables globales.
- [ ] Se respeta el formato estandar de Python PEP8 mediante la aplicación Flake8.
- [ ] Todo dato sensible debe guardarse de manera segura (en un hash o similar).

## Web

- [ ] Utiliza errores HTTP (403, 404, etc).
- [ ] Es multiusuario (puede usarse desde una ventana común y una de incógnito de manera independiente).


## Opcional

- [ ] Utilizar un Framework de Front-End (Vue, React, Angular).
- [ ] Incorporar soporte para múltiples idiomas (L10N y/o I18N).
- [ ] Utilizar Test Unitarios (Pytest).
- [ ] Incorporar Autorización (Roles).
- [ ] El sitio debe ser Responsive o Adaptative (verse bien en dispositivos móviles).
## Estado del proyecto al 10/11/2026

Se conserva arriba el checklist de la cátedra. Las casillas sin marcar no deben interpretarse como ausencia de implementación: el estado comprobable por código es el siguiente.

- [x] Contraseñas almacenadas con PBKDF2-HMAC-SHA256 y salt aleatorio.
- [x] Errores de negocio traducidos a respuestas HTTP.
- [x] Sesiones JWT por contribuyente, con almacenamiento del token en `sessionStorage`.
- [x] Frontend React/TypeScript con estilos adaptables.
- [x] Pruebas pytest de negocio, OCR, seguridad, estadísticas y ARCA.
- [ ] Auditoría completa de nombres y formato con Flake8.
- [ ] Validación manual de navegadores y navegación normal/incógnita.
- [ ] Autorización por roles: no implementada; el aislamiento actual se basa en el CUIT autenticado.
- [ ] Internacionalización: interfaz en español.

Existen constantes y objetos compartidos de configuración; no se acredita el criterio absoluto de ausencia de variables globales. Ver alcance y pendientes en [PROYECTO.md](PROYECTO.md).
