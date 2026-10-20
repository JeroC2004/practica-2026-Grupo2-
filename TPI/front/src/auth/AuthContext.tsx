import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api } from "../api/client";
import type { Contribuyente } from "../types/dominio";

const CLAVE_SESION = "tpi_token";

interface AuthContextValue {
  token: string | null;
  perfil: Contribuyente | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem(CLAVE_SESION));
  const [perfil, setPerfil] = useState<Contribuyente | null>(null);

  useEffect(() => {
    if (!token) {
      setPerfil(null);
      return;
    }
    api
      .obtenerPerfil(token)
      .then(setPerfil)
      .catch(() => setPerfil(null));
  }, [token]);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      perfil,
      login: (nuevoToken: string) => {
        sessionStorage.setItem(CLAVE_SESION, nuevoToken);
        setToken(nuevoToken);
      },
      logout: () => {
        sessionStorage.removeItem(CLAVE_SESION);
        setToken(null);
      },
    }),
    [token, perfil],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const contexto = useContext(AuthContext);
  if (!contexto) {
    throw new Error("useAuth debe usarse dentro de un AuthProvider.");
  }
  return contexto;
}
