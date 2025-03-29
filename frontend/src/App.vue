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
import { ref } from 'vue'
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
