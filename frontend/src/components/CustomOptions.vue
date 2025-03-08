<template>
  <div class="custom-options">
    <el-form :model="form" label-position="top">
      <!-- 提示词输入 -->
      <el-form-item label="风格提示词">
        <el-input
          v-model="form.prompt"
          type="textarea"
          :rows="3"
          placeholder="描述您想要的艺术风格，如：古风、山水画、水墨风等"
          :disabled="loading"
        />
        <div class="form-tip">提示词和参考图至少需要提供一项</div>
      </el-form-item>
      
      <!-- 参考图上传 -->
      <el-form-item label="风格参考图">
        <el-upload
          class="reference-image-uploader"
          action="/api/upload"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          :before-upload="beforeUpload"
          :disabled="loading"
        >
          <img v-if="form.refImageUrl" :src="form.refImageUrl" class="reference-image" />
          <el-icon v-else class="reference-image-uploader-icon"><Plus /></el-icon>
          <div class="el-upload__text">
            点击上传参考图
            <div class="upload-tip">建议图片小于10M，格式为jpg/png/jpeg/bmp</div>
          </div>
        </el-upload>
      </el-form-item>
      
      <!-- 字体设置 -->
      <el-form-item label="字体设置">
        <el-select 
          v-model="form.fontName" 
          placeholder="选择字体" 
          style="width: 100%"
          :disabled="loading"
        >
          <el-option label="古风字体1" value="gufeng1" />
          <el-option label="古风字体2" value="gufeng2" />
          <el-option label="古风字体3" value="gufeng3" />
          <el-option label="古风字体4" value="gufeng4" />
          <el-option label="古风字体5" value="gufeng5" />
        </el-select>
      </el-form-item>
      
      <!-- 字体强度 -->
      <el-form-item label="字体强度">
        <div class="slider-container">
          <span class="slider-label">弱</span>
          <el-slider 
            v-model="form.textStrength" 
            :min="0" 
            :max="1" 
            :step="0.01"
            :disabled="loading"
          />
          <span class="slider-label">强</span>
        </div>
      </el-form-item>
      
      <!-- 字体亮暗 -->
      <el-form-item label="字体亮暗">
        <el-switch
          v-model="form.textInverse"
          :active-text="'亮'"
          :inactive-text="'暗'"
          :disabled="loading"
        />
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { reactive, watch } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'CustomOptions',
  components: {
    Plus
  },
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['custom-options-updated'],
  setup(props, { emit }) {
    const form = reactive({
      prompt: '',
      refImageUrl: null,
      fontName: 'gufeng1',
      textStrength: 0.5,
      textInverse: false
    })
    
    // 监听表单变化，向父组件发送更新
    watch(form, (newValue) => {
      emit('custom-options-updated', { ...newValue })
    }, { deep: true })
    
    // 上传前验证
    const beforeUpload = (file) => {
      const isValidFormat = ['image/jpeg', 'image/png', 'image/bmp'].includes(file.type)
      const isLt10M = file.size / 1024 / 1024 < 10
      
      if (!isValidFormat) {
        ElMessage.error('图片格式不正确，请上传jpg/png/jpeg/bmp格式的图片')
        return false
      }
      
      if (!isLt10M) {
        ElMessage.error('图片大小不能超过10MB')
        return false
      }
      
      return true
    }
    
    // 上传成功回调
    const handleUploadSuccess = (response) => {
      if (response && response.url) {
        form.refImageUrl = response.url
      } else {
        ElMessage.error('上传失败，请重试')
      }
    }
    
    return {
      form,
      beforeUpload,
      handleUploadSuccess
    }
  }
}
</script>

<style scoped>
.custom-options {
  padding: 16px 0;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.reference-image-uploader {
  width: 100%;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.reference-image-uploader:hover {
  border-color: var(--primary-color);
}

.reference-image-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100%;
  height: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.reference-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

.el-upload__text {
  padding: 10px 0;
  text-align: center;
  color: #606266;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider-label {
  font-size: 14px;
  color: #606266;
  width: 30px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-slider) {
  flex: 1;
}
</style> 