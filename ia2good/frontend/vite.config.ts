import react from "@vitejs/plugin-react-swc";
import { defineConfig, PluginOption } from "vite";

// import sparkPlugin from "@github/spark/spark-vite-plugin";
// import createIconImportProxy from "@github/spark/vitePhosphorIconProxyPlugin";
import { resolve } from 'path'
import { fileURLToPath, URL } from 'node:url'

const projectRoot = process.env.PROJECT_ROOT || fileURLToPath(new URL('.', import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  base: process.env.NODE_ENV === 'production' ? '/ia2good/' : '/',
  plugins: [
    react(),
    // DO NOT REMOVE
    // createIconImportProxy() as PluginOption,
    // sparkPlugin() as PluginOption,
  ],
  resolve: {
    alias: {
      '@': resolve(projectRoot, 'src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // Guardian microservice (port 8001) - Security, Missions, Volunteers
      '/api/guardian': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        ws: true,
        rewrite: (path) => path.replace(/^\/api\/guardian/, '')
      },
      '/guardian': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
      
      // EduVerify microservice (port 8002) - Academic verification
      '/api/eduverify': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
        ws: true,
        rewrite: (path) => path.replace(/^\/api\/eduverify/, '/eduverify')
      },
      '/eduverify': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
      
      // MedCare microservice (port 8004) - Medical emergency
      '/api/medcare': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        secure: false,
        ws: true,
        rewrite: (path) => path.replace(/^\/api\/medcare/, '/medcare')
      },
      '/medcare': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
      
      // Fallback for generic API calls (Guardian)
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/health': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      }
    }
  }
});
