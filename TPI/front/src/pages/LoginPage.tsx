import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api, ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function LoginPage() {
  const [cuit, setCuit] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    try {
      const { access_token } = await api.login(cuit, password);
      login(access_token);
      const hoy = new Date();
      navigate(`/libro-iva/${hoy.getFullYear()}/${hoy.getMonth() + 1}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo iniciar sesión.");
    }
  }

  return (
    <div className="pagina angosta">
      <h1>Ingresar</h1>
      <div className="card">
        {error && <p className="error">{error}</p>}
        <form onSubmit={enviar}>
          <label>
            CUIT
            <input value={cuit} onChange={(e) => setCuit(e.target.value)} maxLength={11} minLength={11} required />
          </label>
          <label>
            Contraseña
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          <button type="submit">Ingresar</button>
        </form>
      </div>
      <p className="enlace-secundario">
        ¿No tenés cuenta? <Link to="/registro">Registrate</Link>
      </p>
    </div>
  );
}
