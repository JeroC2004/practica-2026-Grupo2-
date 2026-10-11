import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import { NavBar } from "./components/NavBar";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { RegistroPage } from "./pages/RegistroPage";
import { NuevoComprobantePage } from "./pages/NuevoComprobantePage";
import { LibroIvaPage } from "./pages/LibroIvaPage";

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
      </Route>
      <Route path="/" element={<Inicio />} />
    </Routes>
  );
}

export function App() {
  return (
    <AuthProvider>
      <div className="contenedor">
        <NavBar />
        <Rutas />
      </div>
    </AuthProvider>
  );
}
