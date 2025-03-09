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
        <div class="font-control">
          <el-select 
            v-model="form.fontName" 
            placeholder="选择字体" 
            style="width: 65%"
            :disabled="loading || form.ttfUrl"
          >
            <el-option label="古风字体1" value="gufeng1" />
            <el-option label="古风字体2" value="gufeng2" />
            <el-option label="古风字体3" value="gufeng3" />
            <el-option label="古风字体4" value="gufeng4" />
            <el-option label="古风字体5" value="gufeng5" />
          </el-select>
          
          <el-upload
            class="ttf-uploader"
            action="/api/upload-ttf"
            :show-file-list="false"
            :on-success="handleTtfUploadSuccess"
            :before-upload="beforeTtfUpload"
            :disabled="loading"
            accept=".ttf"
          >
            <el-button 
              size="default" 
              type="primary" 
              :disabled="loading"
              class="upload-btn"
            >
              <el-icon v-if="form.ttfUrl"><Check /></el-icon>
              <el-icon v-else><Upload /></el-icon>
              <span class="btn-text">{{ form.ttfUrl ? '已上传' : '上传字体' }}</span>
            </el-button>
          </el-upload>
        </div>
        <div class="form-tip" v-if="form.ttfUrl">
          已上传自定义字体文件，将优先使用此字体
          <el-button 
            type="text" 
            size="small" 
            @click="clearTtfFile" 
            :disabled="loading"
          >
            清除
          </el-button>
        </div>
        <div class="form-tip" v-else>
          可选择系统字体或上传TTF格式字体文件（小于30MB）
        </div>
      </el-form-item>
      
      <!-- 字体强度 -->
      <el-form-item label="字体强度">
        <div class="strength-control">
          <el-input-number 
            v-model="form.textStrength" 
            :min="1" 
            :max="10" 
            :step="1" 
            :disabled="loading"
            controls-position="right"
            style="width: 90px;"
            size="small"
          />
          <div class="preset-buttons">
            <el-button 
              size="small" 
              :type="form.textStrength === 1 ? 'primary' : 'default'" 
              @click="form.textStrength = 1"
              :disabled="loading"
            >
              极弱
            </el-button>
            <el-button 
              size="small" 
              :type="form.textStrength === 3 ? 'primary' : 'default'" 
              @click="form.textStrength = 3"
              :disabled="loading"
            >
              弱
            </el-button>
            <el-button 
              size="small" 
              :type="form.textStrength === 5 ? 'primary' : 'default'" 
              @click="form.textStrength = 5"
              :disabled="loading"
            >
              中等
            </el-button>
            <el-button 
              size="small" 
              :type="form.textStrength === 7 ? 'primary' : 'default'" 
              @click="form.textStrength = 7"
              :disabled="loading"
            >
              强
            </el-button>
            <el-button 
              size="small" 
              :type="form.textStrength === 10 ? 'primary' : 'default'" 
              @click="form.textStrength = 10"
              :disabled="loading"
            >
              极强
            </el-button>
          </div>
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
import { Plus, Upload, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'CustomOptions',
  components: {
    Plus,
    Upload,
    Check
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
      textStrength: 5,
      textInverse: false,
      ttfUrl: null
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
    
    // TTF文件上传前验证
    const beforeTtfUpload = (file) => {
      const isTTF = file.type === 'font/ttf' || file.name.endsWith('.ttf')
      const isLt30M = file.size / 1024 / 1024 < 30
      
      if (!isTTF) {
        ElMessage.error('请上传TTF格式的字体文件')
        return false
      }
      
      if (!isLt30M) {
        ElMessage.error('字体文件大小不能超过30MB')
        return false
      }
      
      return true
    }
    
    // TTF文件上传成功回调
    const handleTtfUploadSuccess = (response) => {
      if (response && response.url) {
        form.ttfUrl = response.url
        form.fontName = null // 清空字体选择，优先使用上传的字体
        ElMessage.success('字体文件上传成功')
      } else {
        ElMessage.error('上传失败，请重试')
      }
    }
    
    // 清除已上传的TTF文件
    const clearTtfFile = () => {
      form.ttfUrl = null
      form.fontName = 'gufeng1' // 恢复默认字体
    }
    
    return {
      form,
      beforeUpload,
      handleUploadSuccess,
      beforeTtfUpload,
      handleTtfUploadSuccess,
      clearTtfFile
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

.strength-control {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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

.font-control {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.ttf-uploader {
  flex-shrink: 0;
  width: 20%;
}

.upload-btn {
  white-space: nowrap;
  width: 100%;
  text-align: center;
  justify-content: center;
  display: flex;
  align-items: center;
}

.btn-text {
  margin-left: 5px;
}

:deep(.el-button .el-icon) {
  margin-right: 0;
}
</style> 