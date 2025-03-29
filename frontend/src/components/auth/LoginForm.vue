<template>
  <div class="login-form">
    <h2>用户登录</h2>
    <el-form 
      :model="loginForm" 
      :rules="rules" 
      ref="loginFormRef" 
      label-position="top"
      @submit.prevent="handleLogin"
    >
      <el-form-item label="用户名" prop="username">
        <el-input 
          v-model="loginForm.username" 
          placeholder="请输入用户名"
          prefix-icon="User"
        />
      </el-form-item>
      
      <el-form-item label="密码" prop="password">
        <el-input 
          v-model="loginForm.password" 
          type="password" 
          placeholder="请输入密码"
          prefix-icon="Lock"
          show-password
        />
      </el-form-item>
      
      <div class="form-actions">
        <el-button 
          type="primary" 
          native-type="submit" 
          :loading="loading" 
          class="submit-btn"
        >
          登录
        </el-button>
      </div>
      
      <div class="form-footer">
        <span>还没有账号？</span>
        <el-button link @click="$emit('switch-mode', 'register')">
          立即注册
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'LoginForm',
  components: {
    User,
    Lock
  },
  emits: ['login-success', 'switch-mode'],
  setup(props, { emit }) {
    const loginFormRef = ref(null)
    const loading = ref(false)
    
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '密码长度应为6-20个字符', trigger: 'blur' }
      ]
    }
    
    const handleLogin = async () => {
      if (!loginFormRef.value) return
      
      await loginFormRef.value.validate(async (valid) => {
        if (!valid) return
        
        loading.value = true
        
        try {
          console.log('正在发送登录请求到:', '/api/auth/login')
          console.log('登录数据:', loginForm)
          
          const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginForm)
          })
          
          console.log('登录响应状态:', response.status, response.statusText)
          
          // 尝试解析响应
          let responseText
          try {
            responseText = await response.text()
            console.log('响应文本:', responseText)
            
            let data
            if (responseText.trim()) {
              data = JSON.parse(responseText)
              console.log('解析后的数据:', data)
            } else {
              throw new Error('响应为空')
            }
            
            if (!response.ok) {
              throw new Error(data.error || '登录失败')
            }
            
            // 保存令牌到本地存储
            localStorage.setItem('auth_token', data.token)
            localStorage.setItem('user_info', JSON.stringify(data.user))
            
            ElMessage.success('登录成功')
            emit('login-success', data.user)
          } catch (parseError) {
            console.error('解析响应失败:', parseError)
            console.error('原始响应文本:', responseText)
            throw new Error(`解析响应失败: ${parseError.message}`)
          }
        } catch (error) {
          ElMessage.error(error.message || '登录失败，请稍后重试')
          console.error('Login error:', error)
        } finally {
          loading.value = false
        }
      })
    }
    
    return {
      loginFormRef,
      loginForm,
      rules,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 24px;
  color: var(--text-color);
}

.form-actions {
  margin-top: 24px;
}

.submit-btn {
  width: 100%;
  height: 40px;
  font-size: 16px;
}

.form-footer {
  margin-top: 16px;
  text-align: center;
  color: var(--text-color-secondary);
}
</style> 