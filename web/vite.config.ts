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
        manualChunks: {
          maplibre: ["maplibre-gl"],
          recharts: ["recharts"],
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
