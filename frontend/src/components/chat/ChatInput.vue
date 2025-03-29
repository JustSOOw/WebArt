<template>
  <div class="chat-input">
    <div class="card-container" :class="{'has-file': selectedFile}">
      <!-- 隐藏的文本输入框 -->
      <div class="hidden-input">
        <el-input
          v-model="inputContent"
          type="textarea"
          :rows="1"
          :maxlength="2000"
          :disabled="loading"
          ref="inputRef"
          @input="updateHeight"
          @keydown.enter.prevent="handleKeydown"
          @focus="inputFocused = true"
          @blur="handleBlur"
          resize="none"
        />
      </div>
      
      <!-- 卡片显示区域 -->
      <div class="card-content" @click="focusInput">
        <div class="text-display" v-if="inputContent">{{ inputContent }}</div>
        <div class="placeholder" v-else-if="!inputFocused">问问题，尽管问...</div>
      </div>
      
      <!-- 文件信息 - 移到按钮区域前面 -->
      <div class="file-info" v-if="selectedFiles && selectedFiles.length > 0" :class="{'multiple': selectedFiles.length > 1}">
        <el-icon><Document /></el-icon>
        <span class="file-name" :title="getFilesInfo()">
          {{ getShortFileName(selectedFiles[0].name) }}
          <span v-if="selectedFiles.length > 1">+{{ selectedFiles.length - 1 }}个文件</span>
        </span>
        <el-button link @click="clearFiles" class="delete-btn">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
      
      <!-- 按钮区域 -->
      <div class="card-actions">
        <el-upload
          v-if="showUpload"
          class="upload-button"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleFileChange"
          :before-upload="beforeUpload"
          :multiple="true"
        >
          <el-icon><Upload /></el-icon>
        </el-upload>
        
        <div class="send-button" :class="{ 'can-send': canSend }" @click="handleSend">
          <el-icon><Position /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick, onMounted } from 'vue'
import { Upload, Position, Document, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'ChatInput',
  components: {
    Upload,
    Position,
    Document,
    Delete
  },
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    supportedFileTypes: {
      type: Array,
      default: () => []
    },
    maxFileSize: {
      type: Number,
      default: 5 * 1024 * 1024 // 5MB
    },
    showUpload: {
      type: Boolean,
      default: true
    }
  },
  emits: ['send-message', 'upload-file', 'upload-files'],
  setup(props, { emit }) {
    const inputContent = ref('')
    const selectedFile = ref(null)
    const selectedFiles = ref([])
    const inputRef = ref(null)
    const inputFocused = ref(false)
    
    // 计算是否可以发送消息
    const canSend = computed(() => {
      // 必须有文本内容才能发送，即使选择了文件
      return inputContent.value.trim() !== ''
    })
    
    // 聚焦输入框
    const focusInput = () => {
      if (inputRef.value) {
        inputRef.value.focus()
        inputFocused.value = true
      }
    }
    
    // 处理输入框失焦
    const handleBlur = () => {
      // 如果输入框有内容，保持聚焦状态
      // 否则恢复未聚焦状态
      if (!inputContent.value.trim()) {
        inputFocused.value = false
      }
    }
    
    // 更新输入框高度
    const updateHeight = () => {
      if (inputRef.value) {
        const textarea = inputRef.value.$el.querySelector('textarea')
        if (textarea) {
          textarea.style.height = 'auto'
          textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
        }
      }
    }
    
    // 处理文件选择
    const handleFileChange = (file) => {
      // 验证文件类型
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
      if (!props.supportedFileTypes.includes(fileExtension)) {
        ElMessage.error(`不支持的文件类型: ${fileExtension}`)
        return
      }
      
      // 验证文件大小
      if (file.size > props.maxFileSize) {
        ElMessage.error(`文件大小超过限制 (${Math.round(props.maxFileSize / 1024 / 1024)}MB)`)
        return
      }
      
      // 添加到文件列表，但保持兼容性
      selectedFile.value = file
      
      // 对于多文件上传
      if (!selectedFiles.value.some(f => f.uid === file.uid)) {
        selectedFiles.value.push(file)
      }
    }
    
    // 添加beforeUpload方法，防止自动上传
    const beforeUpload = (file) => {
      // 返回false阻止自动上传
      return false
    }
    
    // 清除已选择的文件
    const clearFile = () => {
      selectedFile.value = null
      clearFiles()
    }
    
    // 清除所有文件
    const clearFiles = () => {
      selectedFiles.value = []
      selectedFile.value = null
    }
    
    // 获取文件信息描述
    const getFilesInfo = () => {
      if (!selectedFiles.value.length) return ''
      if (selectedFiles.value.length === 1) return selectedFiles.value[0].name
      return `${selectedFiles.value.length}个文件: ${selectedFiles.value.map(f => f.name).join(', ')}`
    }
    
    // 处理按键
    const handleKeydown = (e) => {
      if (e.shiftKey) {
        // Shift + Enter 换行
        const textarea = e.target
        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        inputContent.value = inputContent.value.substring(0, start) + '\n' + inputContent.value.substring(end)
        // 设置光标位置到换行后
        nextTick(() => {
          textarea.selectionStart = textarea.selectionEnd = start + 1
        })
      } else {
        // Enter 发送
        handleSend()
      }
    }
    
    // 处理发送
    const handleSend = () => {
      if (!canSend.value || props.loading) return
      
      // 获取当前输入框的文本内容
      const content = inputContent.value.trim()
      
      // 如果有多个文件，使用新的方法上传多个文件
      if (selectedFiles.value.length > 1) {
        emit('upload-files', [...selectedFiles.value], content)
        clearFiles()
        // 清空输入内容
        inputContent.value = ''
        // 重置聚焦状态
        inputFocused.value = false
        return
      }
      
      // 如果有单个文件，使用原有方法
      if (selectedFile.value) {
        // 修正：同时传递文件和文本内容
        emit('upload-file', selectedFile.value, content)
        clearFiles()
        // 清空输入内容
        inputContent.value = ''
        // 重置聚焦状态
        inputFocused.value = false
        return
      }
      
      // 发送文本消息
      if (content) {
        emit('send-message', content)
        inputContent.value = ''
        // 重置聚焦状态
        inputFocused.value = false
        // 重新聚焦输入框，以便用户继续输入
        nextTick(() => {
          focusInput()
        })
      }
    }
    
    // 获取简短文件名
    const getShortFileName = (fileName) => {
      if (!fileName) return '';
      if (fileName.length <= 10) return fileName;
      
      const extension = fileName.split('.').pop();
      const baseName = fileName.substring(0, fileName.lastIndexOf('.'));
      return baseName.substring(0, 6) + '...' + extension;
    }
    
    // 组件挂载后自动聚焦
    onMounted(() => {
      nextTick(() => {
        focusInput()
      })
    })
    
    return {
      inputContent,
      selectedFile,
      selectedFiles,
      inputRef,
      inputFocused,
      canSend,
      focusInput,
      handleBlur,
      updateHeight,
      handleFileChange,
      beforeUpload,
      clearFile,
      clearFiles,
      getFilesInfo,
      handleKeydown,
      handleSend,
      getShortFileName,
      Upload,
      Position,
      Document,
      Delete
    }
  }
}
</script>

<style scoped>
.chat-input {
  width: 90%;
  max-width: 640px;
}

.card-container {
  background-color: #fff;
  border-radius: 18px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  padding: 16px;
  position: relative;
  min-height: 56px;
  transition: all 0.3s ease;
}

.card-container.has-file {
  padding-bottom: 50px; /* 为文件信息留出空间 */
}

.card-container:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.hidden-input {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  opacity: 0;
}

.card-content {
  min-height: 24px;
  padding: 6px 60px 6px 10px;
  cursor: text;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}

.text-display {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  color: #333;
}

.placeholder {
  font-size: 14px;
  color: #999;
}

.card-actions {
  position: absolute;
  right: 16px;
  bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: transparent;
  color: #888;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-button:hover {
  background-color: #f3f4f6;
  color: #409eff;
}

.send-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #eee;
  color: #bbb;
  cursor: not-allowed;
  transition: all 0.2s ease;
}

.send-button.can-send {
  background-color: #409eff;
  color: white;
  cursor: pointer;
}

.send-button.can-send:hover {
  background-color: #66b1ff;
}

.file-info {
  display: flex;
  align-items: center;
  position: absolute;
  left: 16px;
  right: 70px; /* 为右侧按钮留出空间 */
  bottom: 12px;
  gap: 4px;
  padding: 2px 8px;
  background-color: #f5f7fa;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  height: 28px;
  max-width: 120px; /* 限制最大宽度 */
}

.file-info.multiple {
  max-width: 140px; /* 对于多文件稍微扩大一点 */
  background-color: #ecf5ff;
}

.file-name {
  font-size: 12px;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 60px; /* 文件名最大宽度 */
}

.file-info.multiple .file-name {
  max-width: 90px;
}

.delete-btn {
  padding: 2px;
  margin: 0;
  height: 20px;
}

@media (max-width: 768px) {
  .chat-input {
    width: 95%;
  }

  .card-container {
    padding: 12px;
  }

  .card-actions {
    right: 12px;
    bottom: 10px;
  }
  
  .file-info {
    left: 12px;
    right: 60px;
  }
}
</style>

