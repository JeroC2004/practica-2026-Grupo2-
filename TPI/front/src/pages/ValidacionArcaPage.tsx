import { useEffect, useState } from "react";
import { CircleAlert, CircleCheck, CircleX } from "lucide-react";
import { api, ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import type { EstadoArca, EstadoArcaTipo } from "../types/dominio";

const ESTADO_INFO: Record<EstadoArcaTipo, { etiqueta: string; clase: string; Icono: typeof CircleCheck }> = {
  confirmado: { etiqueta: "Confirmado en ARCA", clase: "badge-ok", Icono: CircleCheck },
  pendiente: { etiqueta: "Pendiente de emitir", clase: "badge-warn", Icono: CircleAlert },
  no_encontrado_en_arca: { etiqueta: "No encontrado en ARCA", clase: "badge-danger", Icono: CircleX },
};

function hoy(): { anio: number; mes: number } {
  const fecha = new Date();
  return { anio: fecha.getFullYear(), mes: fecha.getMonth() + 1 };
}

export function ValidacionArcaPage() {
  const { token } = useAuth();
  const [periodo] = useState(hoy());
  const [items, setItems] = useState<EstadoArca[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  function cargar() {
    setError(null);
    setItems(null);
    api
      .validarConArca(token!, periodo.anio, periodo.mes)
      .then(setItems)
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo validar contra ARCA."));
  }

  useEffect(cargar, [token, periodo.anio, periodo.mes]);

  const confirmados = items?.filter((i) => i.estado === "confirmado").length ?? 0;
  const pendientes = items?.filter((i) => i.estado === "pendiente").length ?? 0;

  return (
    <div className="pagina ancha">
      <h1>Validar con ARCA — {periodo.mes}/{periodo.anio}</h1>

      <div className="aviso-wip">
        <p className="ayuda">
          Vuelve a consultar en vivo, contra el ambiente de homologación de ARCA, cada venta de este mes que ya
          hayas emitido. Las que todavía no emitiste figuran como pendientes — emitilas desde el Libro de IVA.
        </p>
      </div>

      {error && <p className="error">{error}</p>}

      {items && (
        <div className="resumen">
          <div className="stat">
            <p className="etiqueta">Confirmadas en ARCA</p>
            <p className="valor">{confirmados}</p>
          </div>
          <div className="stat">
            <p className="etiqueta">Pendientes de emitir</p>
            <p className="valor">{pendientes}</p>
          </div>
        </div>
      )}

      {!items && !error && <p className="ayuda">Consultando ARCA...</p>}

      {items && items.length === 0 && <p className="vacio">No hay ventas cargadas este mes.</p>}

      {items && items.length > 0 && (
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
              {items.map((item) => {
                const { etiqueta, clase, Icono } = ESTADO_INFO[item.estado];
                return (
                  <tr key={item.comprobante_id}>
                    <td>
                      <span className="badge">{item.tipo}</span> {String(item.punto_venta).padStart(4, "0")}-
                      {String((item.numero_arca ?? item.numero)).padStart(8, "0")}
                    </td>
                    <td>{item.fecha}</td>
                    <td>
                      <span className={`badge ${clase}`}>
                        <Icono size={13} /> {etiqueta}
                      </span>
                    </td>
                    <td>${item.total.toFixed(2)}</td>
                    <td>{item.total_en_arca != null ? `$${item.total_en_arca.toFixed(2)}` : "—"}</td>
                    <td>{item.cae ?? "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
