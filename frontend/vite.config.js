import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
    hmr: {
      overlay: true,
      clientPort: 5173, // Default Vite dev server port
      host: '0.0.0.0',  // Make HMR available on all network interfaces
    },
    watch: {
      usePolling: true,
      interval: 500,    // More frequent polling (faster updates)
    },
    // Use 0.0.0.0 to make it accessible from outside
    host: '0.0.0.0',
    port: 5173,        // Explicitly set port
    strictPort: false, // Try another port if 5173 is in use
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: true
  }
});