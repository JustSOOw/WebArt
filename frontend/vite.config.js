/*
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-05 22:51:33
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-06 22:21:17
 * @FilePath: \WebArt\frontend\vite.config.js
 * @Description: 
 * 
 * Copyright (c) 2025 by Furdow, All Rights Reserved. 
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000
  },
  build: {
    outDir: 'dist'
  }
}) 