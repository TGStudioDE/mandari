import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  server: {
    host: true,
    port: Number(process.env.PORT) || 5174,
    strictPort: true,
    proxy: {
      '/api': {
        target: process.env.BACKEND_INTERNAL_URL || 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  plugins: [react()],
})


