<template>
  <div class="app-navigation">
    <!-- 导航抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="功能选择"
      direction="ltr"
      size="250px"
      :with-header="true"
    >
      <el-menu
        router
        :default-active="activeRoute"
        class="navigation-menu"
        @select="handleSelect"
      >
        <el-menu-item index="/wordart" route="/wordart">
          <el-icon><Picture /></el-icon>
          <span>百家姓生成</span>
        </el-menu-item>
        <!-- 添加AI对话功能入口 -->
        <el-menu-item index="/chat" route="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI对话</span>
        </el-menu-item>
        <!-- 未来其他功能的导航项将添加在这里 -->
        <el-menu-item index="/video" route="/video">
          <el-icon><VideoPlay /></el-icon>
          <span>视频生成</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>
    
    <!-- 导航切换按钮 -->
    <el-button
      class="navigation-toggle"
      type="primary"
      circle
      @click="toggleDrawer"
    >
      <el-icon><Menu /></el-icon>
    </el-button>

    <!-- Theme Toggle Button -->
    <el-button
      class="theme-toggle-button"
      type="primary"
      @click="toggleTheme"
    >
      Toggle Theme
    </el-button>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Picture, Menu, ChatDotRound, VideoPlay } from '@element-plus/icons-vue'

export default {
  name: 'AppNavigation',
  components: {
    Picture,
    Menu,
    ChatDotRound,
    VideoPlay
  },
  emits: ['navigation-toggle', 'theme-toggle'],
  setup(props, { emit }) {
    const router = useRouter()
    const route = useRoute()
    const drawerVisible = ref(false)
    
    const activeRoute = computed(() => route.path)
    
    const toggleDrawer = () => {
      drawerVisible.value = !drawerVisible.value
      emit('navigation-toggle', drawerVisible.value)
    }
    
    const handleSelect = (index) => {
      // 路由跳转已由el-menu的router属性处理
      drawerVisible.value = false
    }

    const toggleTheme = () => {
      emit('theme-toggle')
    }
    
    return {
      drawerVisible,
      activeRoute,
      toggleDrawer,
      handleSelect,
      toggleTheme
    }
  }
}
</script>

<style scoped>
.app-navigation {
  position: relative;
}

.theme-toggle-button {
  position: fixed;
  top: 150px; /* Adjusted to be below the navigation toggle */
  right: 20px;
  z-index: 999;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.navigation-toggle {
  position: fixed;
  top: 90px;
  right: 20px;
  z-index: 999;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.navigation-menu {
  border-right: none;
}
</style> 