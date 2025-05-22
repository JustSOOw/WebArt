<template>
  <div class="app-wrapper" :class="{ 'dark-theme': currentTheme === 'dark' }">
    <!-- 导航组件 -->
    <app-navigation @navigation-toggle="handleNavigationToggle" @theme-toggle="toggleTheme" />
    
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
    const currentTheme = ref('light') // Initialize currentTheme

    const handleNavigationToggle = (isOpen) => {
      isNavigationOpen.value = isOpen
    }

    const toggleTheme = () => {
      currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
      localStorage.setItem('app-theme', currentTheme.value)
    }

    onMounted(() => {
      const savedTheme = localStorage.getItem('app-theme')
      if (savedTheme) {
        currentTheme.value = savedTheme
      }
    })
    
    return {
      isNavigationOpen,
      handleNavigationToggle,
      currentTheme,
      toggleTheme
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

.dark-theme {
  --primary-color: var(--primary-color-dark);
  --success-color: var(--success-color-dark);
  --warning-color: var(--warning-color-dark);
  --danger-color: var(--danger-color-dark);
  --info-color: var(--info-color-dark);
  --border-color: var(--border-color-dark);
  --background-color: var(--background-color-dark);
  --text-color: var(--text-color-dark);
  --text-color-secondary: var(--text-color-secondary-dark);
  /* Ensure box-shadow also adapts if needed, or is removed/toned down for dark mode */
  --box-shadow: 0 2px 12px rgba(255, 255, 255, 0.1); /* Lighter shadow for dark bg */
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
