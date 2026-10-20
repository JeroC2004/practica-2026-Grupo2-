import { Moon, Sun } from "lucide-react";
import { useTheme } from "../theme/useTheme";

export function ThemeToggle() {
  const { tema, alternarTema } = useTheme();
  const esOscuro = tema === "dark";

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={alternarTema}
      aria-label={esOscuro ? "Cambiar a tema claro" : "Cambiar a tema oscuro"}
      title={esOscuro ? "Tema claro" : "Tema oscuro"}
    >
      {esOscuro ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}
