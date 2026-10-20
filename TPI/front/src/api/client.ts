import type {
  Comprobante,
  ComprobanteIn,
  ComprobanteDetectado,
  Contribuyente,
  CondicionIva,
  EstadoArca,
  LibroIva,
  TokenOut,
} from "../types/dominio";

const BASE_URL = "/api";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}

async function manejarRespuesta<T>(respuesta: Response): Promise<T> {
  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => ({}));
    throw new ApiError(cuerpo.detail ?? respuesta.statusText, respuesta.status);
  }
  return (await respuesta.json()) as T;
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export const api = {
  registrar(datos: {
    cuit: string;
    razon_social: string;
    condicion_iva: CondicionIva;
    password: string;
    confirmacion_password: string;
  }): Promise<Contribuyente> {
    return fetch(`${BASE_URL}/auth/registro`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    }).then((r) => manejarRespuesta<Contribuyente>(r));
  },

  login(cuit: string, password: string): Promise<TokenOut> {
    return fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: cuit, password }),
    }).then((r) => manejarRespuesta<TokenOut>(r));
  },

  obtenerPerfil(token: string): Promise<Contribuyente> {
    return fetch(`${BASE_URL}/auth/me`, { headers: authHeaders(token) }).then((r) =>
      manejarRespuesta<Contribuyente>(r),
    );
  },

  cargarComprobante(token: string, datos: ComprobanteIn): Promise<Comprobante> {
    return fetch(`${BASE_URL}/comprobantes`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify(datos),
    }).then((r) => manejarRespuesta<Comprobante>(r));
  },

  reconocerComprobante(token: string, archivo: File): Promise<ComprobanteDetectado> {
    const datos = new FormData();
    datos.append("archivo", archivo);
    return fetch(`${BASE_URL}/comprobantes/ocr`, {
      method: "POST",
      headers: authHeaders(token),
      body: datos,
    }).then((r) => manejarRespuesta<ComprobanteDetectado>(r));
  },

  obtenerLibroIva(token: string, anio: number, mes: number): Promise<LibroIva> {
    return fetch(`${BASE_URL}/libro-iva/${anio}/${mes}`, { headers: authHeaders(token) }).then((r) =>
      manejarRespuesta<LibroIva>(r),
    );
  },

  emitirEnArca(token: string, comprobanteId: number): Promise<Comprobante> {
    return fetch(`${BASE_URL}/comprobantes/${comprobanteId}/emitir-arca`, {
      method: "POST",
      headers: authHeaders(token),
    }).then((r) => manejarRespuesta<Comprobante>(r));
  },

  validarConArca(token: string, anio: number, mes: number): Promise<EstadoArca[]> {
    return fetch(`${BASE_URL}/validacion-arca/${anio}/${mes}`, { headers: authHeaders(token) }).then((r) =>
      manejarRespuesta<EstadoArca[]>(r),
    );
  },
};
