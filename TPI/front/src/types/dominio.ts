// Espejo manual de TPI/back/views/schemas.py. El proyecto es chico y los dos
// lados cambian juntos; si creciera, convendría generar esto desde /openapi.json.

export const CONDICIONES_IVA = ["monotributo", "responsable_inscripto"] as const;
export type CondicionIva = (typeof CONDICIONES_IVA)[number];

export const TIPOS_COMPROBANTE = ["A", "B", "C", "NC", "ND"] as const;
export type TipoComprobante = (typeof TIPOS_COMPROBANTE)[number];

export const CONDICIONES_COMPROBANTE = ["compra", "venta"] as const;
export type CondicionComprobante = (typeof CONDICIONES_COMPROBANTE)[number];

export interface Contribuyente {
  cuit: string;
  razon_social: string;
  condicion_iva: CondicionIva;
}

export interface TokenOut {
  access_token: string;
  token_type: string;
}

export interface ComprobanteIn {
  tipo: TipoComprobante;
  punto_venta: number;
  numero: number;
  fecha: string; // YYYY-MM-DD
  cuit_contraparte: string;
  neto_gravado: number;
  neto_exento: number;
  iva: number;
  total: number;
  condicion: CondicionComprobante;
}

export interface Comprobante extends ComprobanteIn {
  id: number;
  origen: string;
}

export interface LibroIva {
  cuit_contribuyente: string;
  mes: number;
  anio: number;
  compras: Comprobante[];
  ventas: Comprobante[];
  coeficiente_prorrateo: number;
  credito_fiscal_computable: number;
}
