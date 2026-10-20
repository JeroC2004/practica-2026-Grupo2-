import { LogOut, Menu, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { ThemeToggle } from "./ThemeToggle";

export function TopBar({ onAbrirMenu }: { onAbrirMenu: () => void }) {
  const { token, perfil, logout } = useAuth();
  const navigate = useNavigate();

  if (!token) return null;

  return (
    <header className="topbar">
      <button type="button" className="topbar-menu-btn" onClick={onAbrirMenu} aria-label="Abrir menú">
        <Menu size={20} />
      </button>

      <span className="topbar-marca">Libro de IVA</span>

      <div className="topbar-acciones">
        <ThemeToggle />

        <div className="perfil">
          <span className="perfil-avatar">
            <User size={16} />
          </span>
          <div className="perfil-info">
            <span className="perfil-nombre">{perfil?.razon_social ?? "Cargando..."}</span>
            {perfil && <span className="perfil-cuit">{perfil.cuit}</span>}
          </div>
          <button
            type="button"
            className="btn-link"
            onClick={() => {
              logout();
              navigate("/login");
            }}
            aria-label="Salir"
            title="Salir"
          >
            <LogOut size={17} />
          </button>
        </div>
      </div>
    </header>
  );
}
