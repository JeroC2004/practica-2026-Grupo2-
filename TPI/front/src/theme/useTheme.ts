import { useEffect, useState } from "react";

const CLAVE_TEMA = "tpi_tema";

export type Tema = "dark" | "light";

function leerTemaGuardado(): Tema {
  try {
    return localStorage.getItem(CLAVE_TEMA) === "light" ? "light" : "dark";
  } catch {
    return "dark";
  }
}

/** Oscuro es el default de la app; el usuario puede pasar a claro y queda guardado. */
export function useTheme() {
  const [tema, setTema] = useState<Tema>(leerTemaGuardado);

  useEffect(() => {
    document.documentElement.dataset.theme = tema;
    try {
      localStorage.setItem(CLAVE_TEMA, tema);
    } catch {
      /* localStorage puede fallar en navegación privada: no es crítico. */
    }
  }, [tema]);

  function alternarTema() {
    setTema((previo) => (previo === "dark" ? "light" : "dark"));
  }

  return { tema, alternarTema };
}
