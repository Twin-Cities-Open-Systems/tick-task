import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:7000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        // Function form, not the object form. vite 8 bundles with rolldown
        // rather than rollup, and rolldown rejects an object outright:
        // "TypeError: manualChunks is not a function". Same three chunks,
        // same members.
        //
        // Order matters: 'react-router-dom' and '@tanstack/react-query' both
        // contain 'react', so they must be matched BEFORE the vendor test or
        // they would collapse into it.
        manualChunks(id) {
          if (!id.includes('node_modules')) return;
          // 'react-router', not 'react-router-dom': v6+ react-router-dom is a
          // thin re-export and the actual code resolves under
          // node_modules/react-router/, which does not contain the '-dom'
          // suffix. Matching the longer name put the router in the main
          // bundle instead of its own chunk.
          if (id.includes('react-router')) return 'router';
          if (id.includes('@tanstack/react-query')) return 'query';
          if (id.includes('react-dom') || id.includes('/react/')) return 'vendor';
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
