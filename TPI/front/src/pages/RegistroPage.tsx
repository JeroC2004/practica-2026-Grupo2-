import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../api/client";
import { CONDICIONES_IVA, type CondicionIva } from "../types/dominio";

export function RegistroPage() {
  const [cuit, setCuit] = useState("");
  const [razonSocial, setRazonSocial] = useState("");
  const [condicionIva, setCondicionIva] = useState<CondicionIva>(CONDICIONES_IVA[0]);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    try {
      await api.registrar({ cuit, razon_social: razonSocial, condicion_iva: condicionIva, password });
      navigate("/login");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo completar el registro.");
    }
  }

  return (
    <>
      <h1>Registrarse</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={enviar}>
        <label>
          CUIT (11 dígitos, sin guiones)
          <input value={cuit} onChange={(e) => setCuit(e.target.value)} maxLength={11} minLength={11} required />
        </label>
        <label>
          Razón social
          <input value={razonSocial} onChange={(e) => setRazonSocial(e.target.value)} required />
        </label>
        <label>
          Condición frente al IVA
          <select value={condicionIva} onChange={(e) => setCondicionIva(e.target.value as CondicionIva)}>
            {CONDICIONES_IVA.map((condicion) => (
              <option key={condicion} value={condicion}>
                {condicion}
              </option>
            ))}
          </select>
        </label>
        <label>
          Contraseña
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={6} required />
        </label>
        <button type="submit">Crear cuenta</button>
      </form>
    </>
  );
}
