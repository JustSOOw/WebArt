<template>
  <div class="register-form">
    <h2>用户注册</h2>
    <el-form 
      :model="registerForm" 
      :rules="rules" 
      ref="registerFormRef" 
      label-position="top"
      @submit.prevent="handleRegister"
    >
      <el-form-item label="用户名" prop="username">
        <el-input 
          v-model="registerForm.username" 
          placeholder="请输入用户名"
          prefix-icon="User"
        />
      </el-form-item>
      
      <el-form-item label="邮箱" prop="email">
        <el-input 
          v-model="registerForm.email" 
          placeholder="请输入邮箱"
          prefix-icon="Message"
        />
      </el-form-item>
      
      <el-form-item label="密码" prop="password">
        <el-input 
          v-model="registerForm.password" 
          type="password" 
          placeholder="请输入密码"
          prefix-icon="Lock"
          show-password
        />
      </el-form-item>
      
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input 
          v-model="registerForm.confirmPassword" 
          type="password" 
          placeholder="请再次输入密码"
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
          注册
        </el-button>
      </div>
      
      <div class="form-footer">
        <span>已有账号？</span>
        <el-button type="text" @click="$emit('switch-mode', 'login')">
          立即登录
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'RegisterForm',
  components: {
    User,
    Lock,
    Message
  },
  emits: ['register-success', 'switch-mode'],
  setup(props, { emit }) {
    const registerFormRef = ref(null)
    const loading = ref(false)
    
    const registerForm = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })
    
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else {
        if (registerForm.confirmPassword !== '') {
          registerFormRef.value.validateField('confirmPassword')
        }
        callback()
      }
    }
    
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== registerForm.password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '密码长度应为6-20个字符', trigger: 'blur' },
        { validator: validatePass, trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        { validator: validatePass2, trigger: 'blur' }
      ]
    }
    
    const handleRegister = async () => {
      if (!registerFormRef.value) return
      
      await registerFormRef.value.validate(async (valid) => {
        if (!valid) return
        
        loading.value = true
        
        try {
          const { confirmPassword, ...userData } = registerForm
          
          console.log('正在发送注册请求到:', '/api/auth/register')
          console.log('注册数据:', userData)
          
          // 使用相对路径，让请求从当前域名+路径发出
          const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
          })
          
          console.log('注册响应状态:', response.status, response.statusText)
          
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
              throw new Error(data.error || '注册失败')
            }
            
            // 保存令牌到本地存储
            localStorage.setItem('auth_token', data.token)
            localStorage.setItem('user_info', JSON.stringify(data.user))
            
            ElMessage.success('注册成功')
            emit('register-success', data.user)
          } catch (parseError) {
            console.error('解析响应失败:', parseError)
            console.error('原始响应文本:', responseText)
            throw new Error(`解析响应失败: ${parseError.message}`)
          }
        } catch (error) {
          ElMessage.error(error.message || '注册失败，请稍后重试')
          console.error('Register error:', error)
        } finally {
          loading.value = false
        }
      })
    }
    
    return {
      registerFormRef,
      registerForm,
      rules,
      loading,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-form {
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