import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { TIPOS_COMPROBANTE, CONDICIONES_COMPROBANTE, type TipoComprobante, type CondicionComprobante } from "../types/dominio";

const HOY = new Date().toISOString().slice(0, 10);

export function NuevoComprobantePage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    tipo: TIPOS_COMPROBANTE[0] as TipoComprobante,
    condicion: CONDICIONES_COMPROBANTE[1] as CondicionComprobante, // venta por defecto
    punto_venta: 1,
    numero: 1,
    fecha: HOY,
    cuit_contraparte: "",
    neto_gravado: 0,
    neto_exento: 0,
    iva: 0,
    total: 0,
  });

  function actualizar<K extends keyof typeof form>(campo: K, valor: (typeof form)[K]) {
    setForm((previo) => ({ ...previo, [campo]: valor }));
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    try {
      const comprobante = await api.cargarComprobante(token!, form);
      const [anio, mes] = comprobante.fecha.split("-");
      navigate(`/libro-iva/${anio}/${Number(mes)}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar el comprobante.");
    }
  }

  return (
    <>
      <h1>Cargar comprobante</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={enviar}>
        <label>
          Tipo
          <select value={form.tipo} onChange={(e) => actualizar("tipo", e.target.value as TipoComprobante)}>
            {TIPOS_COMPROBANTE.map((tipo) => (
              <option key={tipo} value={tipo}>
                {tipo}
              </option>
            ))}
          </select>
        </label>
        <label>
          Condición
          <select
            value={form.condicion}
            onChange={(e) => actualizar("condicion", e.target.value as CondicionComprobante)}
          >
            {CONDICIONES_COMPROBANTE.map((condicion) => (
              <option key={condicion} value={condicion}>
                {condicion}
              </option>
            ))}
          </select>
        </label>
        <label>
          Punto de venta
          <input
            type="number"
            min={1}
            value={form.punto_venta}
            onChange={(e) => actualizar("punto_venta", Number(e.target.value))}
            required
          />
        </label>
        <label>
          Número
          <input
            type="number"
            min={1}
            value={form.numero}
            onChange={(e) => actualizar("numero", Number(e.target.value))}
            required
          />
        </label>
        <label>
          Fecha
          <input type="date" value={form.fecha} onChange={(e) => actualizar("fecha", e.target.value)} required />
        </label>
        <label>
          CUIT de la contraparte
          <input
            value={form.cuit_contraparte}
            onChange={(e) => actualizar("cuit_contraparte", e.target.value)}
            maxLength={11}
            minLength={11}
            required
          />
        </label>
        <label>
          Neto gravado
          <input
            type="number"
            step="0.01"
            value={form.neto_gravado}
            onChange={(e) => actualizar("neto_gravado", Number(e.target.value))}
          />
        </label>
        <label>
          Neto exento
          <input
            type="number"
            step="0.01"
            value={form.neto_exento}
            onChange={(e) => actualizar("neto_exento", Number(e.target.value))}
          />
        </label>
        <label>
          IVA
          <input type="number" step="0.01" value={form.iva} onChange={(e) => actualizar("iva", Number(e.target.value))} />
        </label>
        <label>
          Total
          <input
            type="number"
            step="0.01"
            value={form.total}
            onChange={(e) => actualizar("total", Number(e.target.value))}
            required
          />
        </label>
        <button type="submit">Guardar</button>
      </form>
    </>
  );
}
