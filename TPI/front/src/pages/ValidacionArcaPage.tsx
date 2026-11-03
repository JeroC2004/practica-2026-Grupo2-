import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { CircleAlert, CircleCheck, CircleX, FilePlus, TriangleAlert } from "lucide-react";
import { api, ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import type {
  DiferenciaArca,
  EstadoArca,
  EstadoArcaTipo,
  EstadoCompraArca,
  EstadoCompraArcaTipo,
} from "../types/dominio";

type InfoEstado = { etiqueta: string; clase: string; Icono: typeof CircleCheck };

const ESTADO_VENTA: Record<EstadoArcaTipo, InfoEstado> = {
  confirmado: { etiqueta: "Coincide con ARCA", clase: "badge-ok", Icono: CircleCheck },
  con_diferencias: { etiqueta: "Con diferencias", clase: "badge-danger", Icono: TriangleAlert },
  pendiente: { etiqueta: "Pendiente de emitir", clase: "badge-warn", Icono: CircleAlert },
  no_encontrado_en_arca: { etiqueta: "No encontrado en ARCA", clase: "badge-danger", Icono: CircleX },
};

const ESTADO_COMPRA: Record<EstadoCompraArcaTipo, InfoEstado> = {
  confirmado: { etiqueta: "Coincide con ARCA", clase: "badge-ok", Icono: CircleCheck },
  con_diferencias: { etiqueta: "Con diferencias", clase: "badge-danger", Icono: TriangleAlert },
  falta_cargar: { etiqueta: "Falta cargar", clase: "badge-warn", Icono: FilePlus },
  no_encontrado_en_arca: { etiqueta: "No está en ARCA", clase: "badge-danger", Icono: CircleX },
};

const ETIQUETA_CAMPO: Record<DiferenciaArca["campo"], string> = {
  fecha: "Fecha",
  neto: "Neto",
  iva: "IVA",
  total: "Total",
  cae: "CAE",
};

function mesAdyacente(anio: number, mes: number, delta: 1 | -1): [number, number] {
  const fecha = new Date(anio, mes - 1 + delta, 1);
  return [fecha.getFullYear(), fecha.getMonth() + 1];
}

function numeroComprobante(puntoVenta: number, numero: number): string {
  return `${String(puntoVenta).padStart(4, "0")}-${String(numero).padStart(8, "0")}`;
}

function importe(valor: number | null): string {
  return valor != null ? `$${valor.toFixed(2)}` : "—";
}

function Estado({ info, diferencias }: { info: InfoEstado; diferencias: DiferenciaArca[] }) {
  const { etiqueta, clase, Icono } = info;
  return (
    <>
      <span className={`badge ${clase}`}>
        <Icono size={13} /> {etiqueta}
      </span>
      {diferencias.length > 0 && (
        <ul className="diferencias">
          {diferencias.map((d) => (
            <li key={d.campo}>
              <strong>{ETIQUETA_CAMPO[d.campo]}:</strong> local {d.local} · ARCA {d.arca}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

function Contador({ etiqueta, valor }: { etiqueta: string; valor: number }) {
  return (
    <div className="stat">
      <p className="etiqueta">{etiqueta}</p>
      <p className="valor">{valor}</p>
    </div>
  );
}

export function ValidacionArcaPage() {
  const params = useParams<{ anio: string; mes: string }>();
  const { token } = useAuth();
  const [ventas, setVentas] = useState<EstadoArca[] | null>(null);
  const [compras, setCompras] = useState<EstadoCompraArca[] | null>(null);
  const [errorVentas, setErrorVentas] = useState<string | null>(null);
  const [errorCompras, setErrorCompras] = useState<string | null>(null);

  const hoy = new Date();
  const anio = params.anio ? Number(params.anio) : hoy.getFullYear();
  const mes = params.mes ? Number(params.mes) : hoy.getMonth() + 1;

  function cargar() {
    const mensaje = (err: unknown) => (err instanceof ApiError ? err.message : "No se pudo validar contra ARCA.");
    setVentas(null);
    setCompras(null);
    setErrorVentas(null);
    setErrorCompras(null);
    api
      .validarConArca(token!, anio, mes)
      .then(setVentas)
      .catch((err) => setErrorVentas(mensaje(err)));
    api
      .validarComprasConArca(token!, anio, mes)
      .then(setCompras)
      .catch((err) => setErrorCompras(mensaje(err)));
  }

  useEffect(cargar, [token, anio, mes]);

  const contarVentas = (estado: EstadoArcaTipo) => ventas?.filter((i) => i.estado === estado).length ?? 0;
  const contarCompras = (estado: EstadoCompraArcaTipo) => compras?.filter((i) => i.estado === estado).length ?? 0;
  const [anioAnterior, mesAnterior] = mesAdyacente(anio, mes, -1);
  const [anioSiguiente, mesSiguiente] = mesAdyacente(anio, mes, 1);

  return (
    <div className="pagina ancha">
      <h1>
        Validar con ARCA — {mes}/{anio}
      </h1>

      <div className="navegacion-meses">
        <Link to={`/validacion-arca/${anioAnterior}/${mesAnterior}`}>&larr; mes anterior</Link>
        <Link to={`/validacion-arca/${anioSiguiente}/${mesSiguiente}`}>mes siguiente &rarr;</Link>
      </div>

      <h2>Ventas</h2>
      <div className="aviso-wip">
        <p className="ayuda">
          Consulta en vivo, contra el ambiente de homologación de ARCA, cada venta de este mes que ya hayas emitido, y
          compara fecha, neto, IVA, total y CAE con lo que tenés cargado. Las que todavía no emitiste figuran como
          pendientes — emitilas desde el <Link to={`/libro-iva/${anio}/${mes}`}>Libro de IVA</Link>.
        </p>
      </div>

      {errorVentas && <p className="error">{errorVentas}</p>}
      {!ventas && !errorVentas && <p className="ayuda">Consultando ARCA...</p>}

      {ventas && (
        <div className="resumen resumen-4">
          <Contador etiqueta="Coinciden con ARCA" valor={contarVentas("confirmado")} />
          <Contador etiqueta="Con diferencias" valor={contarVentas("con_diferencias")} />
          <Contador etiqueta="No encontradas" valor={contarVentas("no_encontrado_en_arca")} />
          <Contador etiqueta="Pendientes de emitir" valor={contarVentas("pendiente")} />
        </div>
      )}

      {ventas && ventas.length === 0 && <p className="vacio">No hay ventas cargadas este mes.</p>}

      {ventas && ventas.length > 0 && (
        <div className="tabla-wrap">
          <table>
            <thead>
              <tr>
                <th>Comprobante</th>
                <th>Fecha</th>
                <th>Estado</th>
                <th>Mi total</th>
                <th>Total en ARCA</th>
                <th>CAE</th>
              </tr>
            </thead>
            <tbody>
              {ventas.map((item) => (
                <tr key={item.comprobante_id}>
                  <td>
                    <span className="badge">{item.tipo}</span>{" "}
                    {numeroComprobante(item.punto_venta, item.numero_arca ?? item.numero)}
                  </td>
                  <td>{item.fecha}</td>
                  <td>
                    <Estado info={ESTADO_VENTA[item.estado]} diferencias={item.diferencias} />
                  </td>
                  <td>{importe(item.total)}</td>
                  <td>{importe(item.total_en_arca)}</td>
                  <td>{item.cae ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h2>Compras</h2>
      <div className="aviso-wip">
        <p className="ayuda">
          Cruza tus compras cargadas con las facturas que tus proveedores te emitieron en ARCA, en las dos direcciones:
          las que te emitieron y no cargaste, y las que cargaste pero nadie emitió.
        </p>
      </div>

      {errorCompras && <p className="error">{errorCompras}</p>}
      {!compras && !errorCompras && <p className="ayuda">Consultando ARCA...</p>}

      {compras && (
        <div className="resumen resumen-4">
          <Contador etiqueta="Coinciden con ARCA" valor={contarCompras("confirmado")} />
          <Contador etiqueta="Con diferencias" valor={contarCompras("con_diferencias")} />
          <Contador etiqueta="Faltan cargar" valor={contarCompras("falta_cargar")} />
          <Contador etiqueta="No están en ARCA" valor={contarCompras("no_encontrado_en_arca")} />
        </div>
      )}

      {compras && compras.length === 0 && (
        <p className="vacio">No hay compras cargadas ni facturas recibidas este mes.</p>
      )}

      {compras && compras.length > 0 && (
        <div className="tabla-wrap">
          <table>
            <thead>
              <tr>
                <th>Comprobante</th>
                <th>Proveedor</th>
                <th>Fecha</th>
                <th>Estado</th>
                <th>Mi total</th>
                <th>Total en ARCA</th>
              </tr>
            </thead>
            <tbody>
              {compras.map((item) => (
                <tr key={`${item.cuit_emisor}-${item.tipo}-${item.punto_venta}-${item.numero}`}>
                  <td>
                    <span className="badge">{item.tipo}</span> {numeroComprobante(item.punto_venta, item.numero)}
                  </td>
                  <td>{item.cuit_emisor}</td>
                  <td>{item.fecha}</td>
                  <td>
                    <Estado info={ESTADO_COMPRA[item.estado]} diferencias={item.diferencias} />
                  </td>
                  <td>{importe(item.total)}</td>
                  <td>{importe(item.total_en_arca)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
