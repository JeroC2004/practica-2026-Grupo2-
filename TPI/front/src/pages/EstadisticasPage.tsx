import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import type { Estadisticas } from "../types/dominio";

const MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
const moneda = new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" });

export function EstadisticasPage() {
  const { token } = useAuth();
  const [anio, setAnio] = useState(new Date().getFullYear());
  const [anioFiltro, setAnioFiltro] = useState(String(anio));
  const [mes, setMes] = useState(0);
  const [datos, setDatos] = useState<Estadisticas | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setDatos(null);
    setError(null);
    api.obtenerEstadisticas(token!, anio, controller.signal)
      .then((respuesta) => { if (!controller.signal.aborted) setDatos(respuesta); })
      .catch((err) => {
        if (!controller.signal.aborted) setError(err instanceof ApiError ? err.message : "No se pudieron cargar las estadísticas.");
      });
    return () => controller.abort();
  }, [token, anio, intento]);

  const filas = datos?.meses.filter((fila) => mes === 0 || fila.mes === mes) ?? [];
  const totales = filas.reduce((total, fila) => ({
    compras: total.compras + fila.compras,
    ventas: total.ventas + fila.ventas,
    cantidad_compras: total.cantidad_compras + fila.cantidad_compras,
    cantidad_ventas: total.cantidad_ventas + fila.cantidad_ventas,
  }), { compras: 0, ventas: 0, cantidad_compras: 0, cantidad_ventas: 0 });
  const maximo = Math.max(1, ...filas.flatMap((fila) => [Math.abs(fila.compras), Math.abs(fila.ventas)]));

  return (
    <div className="pagina ancha">
      <h1>Estadísticas de compras y ventas</h1>
      <form className="card estadisticas-filtros" onSubmit={(event) => {
        event.preventDefault();
        setAnio(Number(anioFiltro));
        setIntento((valor) => valor + 1);
      }}>
        <label>Año
          <input type="number" min="1" max="9998" step="1" required value={anioFiltro} onChange={(event) => setAnioFiltro(event.target.value)} />
        </label>
        <label>Mes
          <select value={mes} onChange={(event) => setMes(Number(event.target.value))}>
            <option value={0}>Todo el año</option>
            {MESES.map((nombre, indice) => <option key={nombre} value={indice + 1}>{nombre}</option>)}
          </select>
        </label>
        <button type="submit">Consultar</button>
      </form>

      {error ? <p className="error" role="alert">{error} Volvé a intentar con Consultar.</p> : !datos ?
        <p className="ayuda" role="status">Cargando estadísticas...</p> : <>
        <h2>{mes === 0 ? "Todo el año" : MESES[mes - 1]} · {datos.anio}</h2>
        <div className="resumen resumen-4">
          <div className="stat"><p className="etiqueta">Total de ventas</p><p className="valor">{moneda.format(totales.ventas)}</p></div>
          <div className="stat"><p className="etiqueta">Total de compras</p><p className="valor">{moneda.format(totales.compras)}</p></div>
          <div className="stat"><p className="etiqueta">Diferencia ventas − compras</p><p className="valor">{moneda.format(totales.ventas - totales.compras)}</p></div>
          <div className="stat"><p className="etiqueta">Comprobantes</p><p className="valor">{totales.cantidad_ventas + totales.cantidad_compras}</p><p className="ayuda">{totales.cantidad_ventas} ventas · {totales.cantidad_compras} compras</p></div>
        </div>
        <p className="ayuda">Importes en pesos, con IVA incluido. Las notas de crédito se restan de los totales y cuentan como comprobantes. La diferencia no representa la ganancia.</p>
        {totales.cantidad_compras + totales.cantidad_ventas === 0 && <p className="vacio">No hay compras ni ventas registradas en este período.</p>}

        <h2>Comparación por mes</h2>
        <p className="ayuda">Ventas: verde · Compras: naranja. Las barras muestran la magnitud del importe; los valores conservan su signo.</p>
        <div className="card estadisticas-grafico">
          {filas.map((fila) => <div key={fila.mes} className="estadisticas-mes">
            <strong>{MESES[fila.mes - 1]}</strong>
            <div className="estadisticas-barra"><span>Ventas</span><div className="estadisticas-pista" aria-hidden="true"><div className="estadisticas-venta" style={{ width: `${Math.abs(fila.ventas) / maximo * 100}%` }} /></div><span>{moneda.format(fila.ventas)}</span></div>
            <div className="estadisticas-barra"><span>Compras</span><div className="estadisticas-pista" aria-hidden="true"><div className="estadisticas-compra" style={{ width: `${Math.abs(fila.compras) / maximo * 100}%` }} /></div><span>{moneda.format(fila.compras)}</span></div>
          </div>)}
        </div>

        <h2>Detalle mensual</h2>
        <div className="tabla-wrap">
          <table>
            <caption className="sr-only">Compras y ventas de {datos.anio}</caption>
            <thead><tr><th scope="col">Mes</th><th scope="col">Ventas</th><th scope="col">Compras</th><th scope="col">Cant. ventas</th><th scope="col">Cant. compras</th><th scope="col">Diferencia</th><th scope="col">Detalle</th></tr></thead>
            <tbody>{filas.map((fila) => <tr key={fila.mes}>
              <td>{MESES[fila.mes - 1]}</td><td>{moneda.format(fila.ventas)}</td><td>{moneda.format(fila.compras)}</td><td>{fila.cantidad_ventas}</td><td>{fila.cantidad_compras}</td><td>{moneda.format(fila.ventas - fila.compras)}</td>
              <td><Link className="text-primary hover:underline" to={`/libro-iva/${datos.anio}/${fila.mes}`}>Ver comprobantes</Link></td>
            </tr>)}</tbody>
          </table>
        </div>
      </>}
    </div>
  );
}
