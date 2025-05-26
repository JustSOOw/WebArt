<!--
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-05 22:52:14
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-05-26 14:47:01
 * @FilePath: \WebArt\frontend\src\App.vue
 * @Description: 
 * 
 * Copyright (c) 2025 by Furdow, All Rights Reserved. 
-->
<template>
  <div class="app-wrapper">
    <!-- 导航组件 -->
    <app-navigation @navigation-toggle="handleNavigationToggle" />
    
    <!-- 路由视图容器 -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
            </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import AppNavigation from './components/common/AppNavigation.vue'

export default {
  name: 'App',
  components: {
    AppNavigation
  },
  setup() {
    const isNavigationOpen = ref(false)

    const handleNavigationToggle = (isOpen) => {
      isNavigationOpen.value = isOpen
    }

    return {
      isNavigationOpen,
      handleNavigationToggle
    }
  }
}
</script>

<style>
/* 全局样式 */
:root {
  --primary-color: #409EFF;
  --success-color: #67C23A;
  --warning-color: #E6A23C;
  --danger-color: #F56C6C;
  --info-color: #909399;
  --border-color: #EBEEF5;
  --background-color: #F5F7FA;
  --text-color: #303133;
  --text-color-secondary: #606266;
  --border-radius: 12px;
  --box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

  /* Dark Theme Variables */
  --primary-color-dark: #79bbff;
  --success-color-dark: #85ce61;
  --warning-color-dark: #ebb563;
  --danger-color-dark: #f78989;
  --info-color-dark: #a6a9ad;
  --border-color-dark: #4C4C4C;
  --background-color-dark: #121212;
  --text-color-dark: #E0E0E0;
  --text-color-secondary-dark: #B0B0B0;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.5;
}

.app-wrapper {
  width: 100%;
  min-height: 100vh;
}

/* 路由转场动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
