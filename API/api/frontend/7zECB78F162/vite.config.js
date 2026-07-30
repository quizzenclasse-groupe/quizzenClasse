// vite.config.js
// Configuration minimale de Vite (mêmes choix que Quiz_app : React + port
// de développement standard 5173, cohérent avec CORS_ORIGINS côté API).
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
