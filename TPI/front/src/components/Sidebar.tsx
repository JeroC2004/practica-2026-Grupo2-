import { Link, useLocation } from "react-router-dom";
import { ChevronLeft, ChevronRight, FilePlus2, LayoutDashboard, ShieldCheck } from "lucide-react";
import { useAuth } from "../auth/AuthContext";

const ITEMS = [
  { to: "/", etiqueta: "Inicio", Icono: LayoutDashboard, activo: (p: string) => p === "/" || p.startsWith("/libro-iva") },
  { to: "/comprobantes/nuevo", etiqueta: "Nuevo comprobante", Icono: FilePlus2, activo: (p: string) => p.startsWith("/comprobantes") },
  { to: "/validacion-arca", etiqueta: "Validar con ARCA", Icono: ShieldCheck, activo: (p: string) => p.startsWith("/validacion-arca") },
];

interface Props {
  colapsado: boolean;
  onToggle: () => void;
  abiertoMobile: boolean;
  onCerrarMobile: () => void;
}

export function Sidebar({ colapsado, onToggle, abiertoMobile, onCerrarMobile }: Props) {
  const { token } = useAuth();
  const { pathname } = useLocation();

  if (!token) return null;

  const mostrarEtiquetas = abiertoMobile || !colapsado;

  return (
    <>
      {abiertoMobile && <div className="sidebar-backdrop" onClick={onCerrarMobile} />}

      <aside className={`sidebar ${abiertoMobile ? "sidebar-visible-mobile" : "sidebar-oculto-mobile"} ${colapsado ? "sidebar-colapsado" : ""}`}>
        <button
          type="button"
          className="sidebar-toggle"
          onClick={onToggle}
          aria-label={colapsado ? "Expandir menú" : "Contraer menú"}
          title={colapsado ? "Expandir menú" : "Contraer menú"}
        >
          {colapsado ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>

        <nav className="sidebar-nav">
          {ITEMS.map(({ to, etiqueta, Icono, activo }) => (
            <Link
              key={to}
              to={to}
              onClick={onCerrarMobile}
              className={`sidebar-item ${activo(pathname) ? "sidebar-item-activo" : ""}`}
              title={etiqueta}
            >
              <Icono size={19} strokeWidth={2} />
              {mostrarEtiquetas && <span>{etiqueta}</span>}
            </Link>
          ))}
        </nav>
      </aside>
    </>
  );
}
