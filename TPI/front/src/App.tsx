import { useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import { Sidebar } from "./components/Sidebar";
import { TopBar } from "./components/TopBar";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { RegistroPage } from "./pages/RegistroPage";
import { NuevoComprobantePage } from "./pages/NuevoComprobantePage";
import { LibroIvaPage } from "./pages/LibroIvaPage";
import { ValidacionArcaPage } from "./pages/ValidacionArcaPage";

const CLAVE_SIDEBAR_COLAPSADO = "tpi_sidebar_colapsado";

function Inicio() {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  const hoy = new Date();
  return <Navigate to={`/libro-iva/${hoy.getFullYear()}/${hoy.getMonth() + 1}`} replace />;
}

function Rutas() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/registro" element={<RegistroPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/comprobantes/nuevo" element={<NuevoComprobantePage />} />
        <Route path="/libro-iva/:anio/:mes" element={<LibroIvaPage />} />
        <Route path="/validacion-arca" element={<ValidacionArcaPage />} />
      </Route>
      <Route path="/" element={<Inicio />} />
    </Routes>
  );
}

function Layout() {
  const [colapsado, setColapsado] = useState(() => {
    try {
      return localStorage.getItem(CLAVE_SIDEBAR_COLAPSADO) === "1";
    } catch {
      return false;
    }
  });
  const [abiertoMobile, setAbiertoMobile] = useState(false);

  function alternarColapsado() {
    setColapsado((previo) => {
      const nuevo = !previo;
      try {
        localStorage.setItem(CLAVE_SIDEBAR_COLAPSADO, nuevo ? "1" : "0");
      } catch {
        /* localStorage puede fallar en navegación privada: no es crítico. */
      }
      return nuevo;
    });
  }

  return (
    <div className="app-shell">
      <TopBar onAbrirMenu={() => setAbiertoMobile(true)} />
      <div className="app-body">
        <Sidebar
          colapsado={colapsado}
          onToggle={alternarColapsado}
          abiertoMobile={abiertoMobile}
          onCerrarMobile={() => setAbiertoMobile(false)}
        />
        <main className="contenido">
          <Rutas />
        </main>
      </div>
    </div>
  );
}

export function App() {
  return (
    <AuthProvider>
      <Layout />
    </AuthProvider>
  );
}
