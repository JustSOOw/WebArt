<template>
  <div class="user-profile">
    <el-dropdown trigger="click" @command="handleCommand">
      <div class="user-avatar">
        <el-avatar :size="40" :src="avatarUrl">
          {{ userInitials }}
        </el-avatar>
        <span class="username">{{ user.username }}</span>
        <el-icon><ArrowDown /></el-icon>
      </div>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="profile">
            <el-icon><User /></el-icon>
            <span>个人资料</span>
          </el-dropdown-item>
          <el-dropdown-item command="history">
            <el-icon><Picture /></el-icon>
            <span>我的图片</span>
          </el-dropdown-item>
          <el-dropdown-item divided command="logout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
    
    <!-- 个人资料对话框 -->
    <el-dialog
      v-model="profileDialogVisible"
      title="个人资料"
      width="400px"
    >
      <div class="profile-info">
        <el-avatar :size="80" :src="avatarUrl" class="large-avatar">
          {{ userInitials }}
        </el-avatar>
        <h3>{{ user.username }}</h3>
        <p class="email">{{ user.email }}</p>
        <p class="join-date">注册时间: {{ formatDate(user.created_at) }}</p>
        <p v-if="user.last_login" class="login-date">
          上次登录: {{ formatDate(user.last_login) }}
        </p>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Picture, SwitchButton, ArrowDown } from '@element-plus/icons-vue'

export default {
  name: 'UserProfile',
  components: {
    User,
    Picture,
    SwitchButton,
    ArrowDown
  },
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  emits: ['logout', 'show-history'],
  setup(props, { emit }) {
    const profileDialogVisible = ref(false)
    
    // 计算用户头像URL或初始字母
    const avatarUrl = computed(() => {
      // 这里可以根据用户ID或用户名生成头像URL
      // 例如使用Gravatar或其他头像服务
      return null
    })
    
    const userInitials = computed(() => {
      if (!props.user || !props.user.username) return '?'
      return props.user.username.charAt(0).toUpperCase()
    })
    
    const handleCommand = (command) => {
      switch (command) {
        case 'profile':
          profileDialogVisible.value = true
          break
        case 'history':
          emit('show-history')
          break
        case 'logout':
          confirmLogout()
          break
      }
    }
    
    const confirmLogout = () => {
      ElMessageBox.confirm(
        '确定要退出登录吗？',
        '退出登录',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        // 清除本地存储的用户信息和令牌
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_info')
        
        // 通知父组件用户已登出
        emit('logout')
        
        ElMessage.success('已退出登录')
      }).catch(() => {
        // 用户取消操作
      })
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    return {
      profileDialogVisible,
      avatarUrl,
      userInitials,
      handleCommand,
      formatDate
    }
  }
}
</script>

<style scoped>
.user-avatar {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.user-avatar:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.large-avatar {
  margin-bottom: 16px;
}

.profile-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: var(--text-color);
}

.email {
  color: var(--text-color-secondary);
  margin-bottom: 16px;
}

.join-date, .login-date {
  font-size: 14px;
  color: var(--text-color-secondary);
  margin: 4px 0;
}
</style> 