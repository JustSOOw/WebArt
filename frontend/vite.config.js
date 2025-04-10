/*
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-05 22:51:33
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-04-09 14:17:47
 * @FilePath: \WebArt\frontend\vite.config.js
 * @Description: 
 * 
 * Copyright (c) 2025 by Furdow, All Rights Reserved. 
 */
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// Load env file based on mode (development, production)
// Note: We are loading from the directory where the command runs (root), 
// but our .env.dev is in ./backend. This won't work directly.
// We rely on docker-compose injecting VITE_PUBLIC_BASE_URL into the container env.

export default defineConfig(({ mode }) => {
  // Load env vars based on mode and prefix VITE_
  // Vite automatically loads .env files in the root, but we need to access the one provided by Docker Compose.
  // So, we'll directly use process.env populated by Docker Compose
  const env = { ...process.env }; // Use process.env directly

  return {
    plugins: [vue()],
    server: {
      port: 3000,
      host: '0.0.0.0',
      allowedHosts: (() => {
        const hosts = ['localhost'];
        // Read from process.env now
        const publicBaseUrl = env.VITE_PUBLIC_BASE_URL;
        if (publicBaseUrl) {
          try {
            const url = new URL(publicBaseUrl);
            hosts.push(url.hostname);
          } catch (e) {
            // Log a warning if the URL is invalid, but don't crash
            console.warn(`[vite.config.js] Invalid VITE_PUBLIC_BASE_URL: "${publicBaseUrl}". Could not add hostname to allowedHosts.`);
          }
        }
        return hosts;
      })(),
      watch: {
        usePolling: true
      },
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          secure: false
        }
      }
    },
    build: {
      outDir: 'dist'
    }
  }
}) 