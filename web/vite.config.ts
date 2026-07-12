import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves from a repo subpath; override with VITE_BASE if needed.
export default defineConfig({
  base: process.env.VITE_BASE ?? "/",
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        // The two heavy libraries dwarf the app code; splitting them out keeps
        // the main chunk small and lets the browser cache them across deploys.
        // Function form: Vite 8 (Rolldown) no longer accepts the object form.
        manualChunks(id: string) {
          if (id.includes("node_modules/maplibre-gl/")) return "maplibre";
          if (id.includes("node_modules/recharts/")) return "recharts";
        },
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
    setupFiles: ["tests/setup.tsx"],
  },
});
