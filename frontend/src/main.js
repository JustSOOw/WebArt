/*
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-05 22:52:01
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-20 18:03:44
 * @FilePath: \WebArt\frontend\src\main.js
 * @Description: 
 * 
 * Copyright (c) 2025 by Furdow, All Rights Reserved. 
 */
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './assets/styles/global.css'

const app = createApp(App)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(ElementPlus)
app.mount('#app') 