import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
const base = process.env.APP_BASE_PATH || "/";

// https://vitejs.dev/config/
export default defineConfig({
  base,
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
