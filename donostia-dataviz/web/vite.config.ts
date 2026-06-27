import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves from a repo subpath; override with VITE_BASE if needed.
export default defineConfig({
  base: process.env.VITE_BASE ?? "/",
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
  },
});
