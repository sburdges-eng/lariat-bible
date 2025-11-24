import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Use relative paths for Electron file:// protocol
  base: './',
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    // Ensure assets work in Electron
    assetsDir: 'assets',
    // Generate source maps for debugging
    sourcemap: false,
  },
});
