<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="500px"
    :close-on-click-modal="false"
    :show-close="true"
    @closed="handleDialogClosed"
  >
    <login-form
      v-if="mode === 'login'"
      @login-success="handleAuthSuccess"
      @switch-mode="switchMode"
    />
    <register-form
      v-else-if="mode === 'register'"
      @register-success="handleAuthSuccess"
      @switch-mode="switchMode"
    />
  </el-dialog>
</template>

<script>
import { ref, computed } from 'vue'
import LoginForm from './LoginForm.vue'
import RegisterForm from './RegisterForm.vue'

export default {
  name: 'UserDialog',
  components: {
    LoginForm,
    RegisterForm
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    initialMode: {
      type: String,
      default: 'login',
      validator: (value) => ['login', 'register'].includes(value)
    }
  },
  emits: ['update:visible', 'auth-success'],
  setup(props, { emit }) {
    const mode = ref(props.initialMode)
    
    const dialogVisible = computed({
      get: () => props.visible,
      set: (value) => emit('update:visible', value)
    })
    
    const dialogTitle = computed(() => {
      return mode.value === 'login' ? '用户登录' : '用户注册'
    })
    
    const switchMode = (newMode) => {
      mode.value = newMode
    }
    
    const handleAuthSuccess = (user) => {
      emit('auth-success', user)
      dialogVisible.value = false
    }
    
    const handleDialogClosed = () => {
      // 重置为初始模式
      mode.value = props.initialMode
    }
    
    return {
      mode,
      dialogVisible,
      dialogTitle,
      switchMode,
      handleAuthSuccess,
      handleDialogClosed
    }
  }
}
</script>

<style scoped>
:deep(.el-dialog__header) {
  text-align: center;
  padding-bottom: 0;
}

:deep(.el-dialog__body) {
  padding-top: 10px;
}
</style> 