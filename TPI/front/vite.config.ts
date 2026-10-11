import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En desarrollo, Vite proxea /api al backend de FastAPI: así el front nunca
// hace un request cross-origin y no hace falta configurar CORS en ningún entorno.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
