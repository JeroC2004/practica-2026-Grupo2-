import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

const CLAVE_SESION = "tpi_token";

interface AuthContextValue {
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem(CLAVE_SESION));

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      login: (nuevoToken: string) => {
        sessionStorage.setItem(CLAVE_SESION, nuevoToken);
        setToken(nuevoToken);
      },
      logout: () => {
        sessionStorage.removeItem(CLAVE_SESION);
        setToken(null);
      },
    }),
    [token],
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
