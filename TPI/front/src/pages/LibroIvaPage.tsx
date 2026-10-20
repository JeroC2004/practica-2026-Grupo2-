import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import type { Comprobante, LibroIva } from "../types/dominio";

function mesAdyacente(anio: number, mes: number, delta: 1 | -1): [number, number] {
  const fecha = new Date(anio, mes - 1 + delta, 1);
  return [fecha.getFullYear(), fecha.getMonth() + 1];
}

interface PropsTabla {
  comprobantes: Comprobante[];
  mostrarArca?: boolean;
  emitiendoId?: number | null;
  onEmitir?: (comprobanteId: number) => void;
}

function TablaComprobantes({ comprobantes, mostrarArca, emitiendoId, onEmitir }: PropsTabla) {
  if (comprobantes.length === 0) return <p className="vacio">Sin comprobantes cargados este mes.</p>;
  return (
    <div className="tabla-wrap">
      <table>
        <thead>
          <tr>
            <th>Comprobante</th>
            <th>Fecha</th>
            <th>Contraparte</th>
            <th>Gravado</th>
            <th>Exento</th>
            <th>IVA</th>
            <th>Total</th>
            {mostrarArca && <th>ARCA</th>}
          </tr>
        </thead>
        <tbody>
          {comprobantes.map((c) => (
            <tr key={c.id}>
              <td>
                <span className="badge">{c.tipo}</span> {String(c.punto_venta).padStart(4, "0")}-
                {String(c.numero).padStart(8, "0")}
              </td>
              <td>{c.fecha}</td>
              <td>{c.cuit_contraparte}</td>
              <td>{c.neto_gravado.toFixed(2)}</td>
              <td>{c.neto_exento.toFixed(2)}</td>
              <td>{c.iva.toFixed(2)}</td>
              <td>{c.total.toFixed(2)}</td>
              {mostrarArca && (
                <td>
                  {c.cae ? (
                    <span className="badge badge-ok" title={`CAE ${c.cae} · vence ${c.cae_vencimiento}`}>
                      Emitido
                    </span>
                  ) : (
                    <button
                      type="button"
                      className="btn-secundario"
                      disabled={emitiendoId === c.id}
                      onClick={() => onEmitir?.(c.id)}
                    >
                      {emitiendoId === c.id ? "Emitiendo..." : "Emitir en ARCA"}
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function LibroIvaPage() {
  const { anio, mes } = useParams<{ anio: string; mes: string }>();
  const { token } = useAuth();
  const [libro, setLibro] = useState<LibroIva | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [emitiendoId, setEmitiendoId] = useState<number | null>(null);

  const anioNum = Number(anio);
  const mesNum = Number(mes);

  function cargarLibro() {
    setError(null);
    api
      .obtenerLibroIva(token!, anioNum, mesNum)
      .then(setLibro)
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo cargar el libro de IVA."));
  }

  useEffect(cargarLibro, [token, anioNum, mesNum]);

  async function emitirEnArca(comprobanteId: number) {
    setEmitiendoId(comprobanteId);
    setError(null);
    try {
      await api.emitirEnArca(token!, comprobanteId);
      cargarLibro();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo emitir el comprobante en ARCA.");
    } finally {
      setEmitiendoId(null);
    }
  }

  const [anioAnterior, mesAnterior] = mesAdyacente(anioNum, mesNum, -1);
  const [anioSiguiente, mesSiguiente] = mesAdyacente(anioNum, mesNum, 1);

  if (error) return <p className="error">{error}</p>;
  if (!libro) return <p className="ayuda">Cargando...</p>;

  return (
    <div className="pagina ancha">
      <h1>
        Libro de IVA — {libro.mes}/{libro.anio}
      </h1>

      <div className="navegacion-meses">
        <Link to={`/libro-iva/${anioAnterior}/${mesAnterior}`}>&larr; mes anterior</Link>
        <Link to={`/libro-iva/${anioSiguiente}/${mesSiguiente}`}>mes siguiente &rarr;</Link>
      </div>

      <div className="resumen">
        <div className="stat">
          <p className="etiqueta">Coeficiente de prorrateo (acumulado del ejercicio)</p>
          <p className="valor">{libro.coeficiente_prorrateo.toFixed(4)}</p>
        </div>
        <div className="stat">
          <p className="etiqueta">Crédito fiscal computable del mes</p>
          <p className="valor">${libro.credito_fiscal_computable.toFixed(2)}</p>
        </div>
      </div>

      <h2>Ventas</h2>
      <TablaComprobantes
        comprobantes={libro.ventas}
        mostrarArca
        emitiendoId={emitiendoId}
        onEmitir={emitirEnArca}
      />

      <h2>Compras</h2>
      <TablaComprobantes comprobantes={libro.compras} />
    </div>
  );
}
