import { defineConfig } from "vite";
import solid from "vite-plugin-solid";

export default defineConfig({
  plugins: [solid()],
  server: {
    port: 816,
    proxy: {
      "/api": {
        target: "http://localhost:8000", // backend FastAPI
        changeOrigin: true,
      },
    },
  },
});
