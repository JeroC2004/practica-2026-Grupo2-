import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function NavBar() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();

  if (!token) return null;

  return (
    <nav>
      <Link to="/">Inicio</Link>
      <Link to="/comprobantes/nuevo">Nuevo comprobante</Link>
      <button
        type="button"
        onClick={() => {
          logout();
          navigate("/login");
        }}
      >
        Salir
      </button>
    </nav>
  );
}
