import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import type { Comprobante, LibroIva } from "../types/dominio";

function mesAdyacente(anio: number, mes: number, delta: 1 | -1): [number, number] {
  const fecha = new Date(anio, mes - 1 + delta, 1);
  return [fecha.getFullYear(), fecha.getMonth() + 1];
}

function TablaComprobantes({ comprobantes }: { comprobantes: Comprobante[] }) {
  if (comprobantes.length === 0) return <p>Sin comprobantes cargados este mes.</p>;
  return (
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
        </tr>
      </thead>
      <tbody>
        {comprobantes.map((c) => (
          <tr key={c.id}>
            <td>
              {c.tipo} {String(c.punto_venta).padStart(4, "0")}-{String(c.numero).padStart(8, "0")}
            </td>
            <td>{c.fecha}</td>
            <td>{c.cuit_contraparte}</td>
            <td>{c.neto_gravado.toFixed(2)}</td>
            <td>{c.neto_exento.toFixed(2)}</td>
            <td>{c.iva.toFixed(2)}</td>
            <td>{c.total.toFixed(2)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function LibroIvaPage() {
  const { anio, mes } = useParams<{ anio: string; mes: string }>();
  const { token } = useAuth();
  const [libro, setLibro] = useState<LibroIva | null>(null);
  const [error, setError] = useState<string | null>(null);

  const anioNum = Number(anio);
  const mesNum = Number(mes);

  useEffect(() => {
    setError(null);
    api
      .obtenerLibroIva(token!, anioNum, mesNum)
      .then(setLibro)
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo cargar el libro de IVA."));
  }, [token, anioNum, mesNum]);

  const [anioAnterior, mesAnterior] = mesAdyacente(anioNum, mesNum, -1);
  const [anioSiguiente, mesSiguiente] = mesAdyacente(anioNum, mesNum, 1);

  if (error) return <p className="error">{error}</p>;
  if (!libro) return <p>Cargando...</p>;

  return (
    <>
      <h1>
        Libro de IVA — {libro.mes}/{libro.anio}
      </h1>
      <p>
        <Link to={`/libro-iva/${anioAnterior}/${mesAnterior}`}>&larr; mes anterior</Link>
        &nbsp;|&nbsp;
        <Link to={`/libro-iva/${anioSiguiente}/${mesSiguiente}`}>mes siguiente &rarr;</Link>
      </p>

      <div className="resumen">
        <strong>Coeficiente de prorrateo (acumulado del ejercicio):</strong> {libro.coeficiente_prorrateo.toFixed(4)}
        <br />
        <strong>Crédito fiscal computable del mes:</strong> ${libro.credito_fiscal_computable.toFixed(2)}
      </div>

      <h2>Ventas</h2>
      <TablaComprobantes comprobantes={libro.ventas} />

      <h2>Compras</h2>
      <TablaComprobantes comprobantes={libro.compras} />
    </>
  );
}
