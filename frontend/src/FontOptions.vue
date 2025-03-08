<template>
  <div class="font-options">
    <div class="section-header">
      <el-icon><Document /></el-icon>
      <span>选择字体</span>
    </div>
    
    <div class="font-content">
      <div class="font-selection">
        <el-radio-group v-model="selectedFont" class="font-radio-group">
          <el-radio label="宋体">宋体</el-radio>
          <el-radio label="楷体">楷体</el-radio>
        </el-radio-group>
      </div>
      
      <div class="upload-section">
        <p>选择您的字体文件</p>
        <el-upload
          class="font-uploader"
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :limit="1"
        >
          <el-button type="primary" plain>
            <el-icon><Upload /></el-icon>
            点击上传
          </el-button>
          <template #tip>
            <div class="el-upload__tip">
              支持的字体文件格式：.ttf, .otf
            </div>
          </template>
        </el-upload>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { Document, Upload } from '@element-plus/icons-vue'

export default {
  name: 'FontOptions',
  components: {
    Document,
    Upload
  },
  setup(props, { emit }) {
    const selectedFont = ref('宋体')    //ref创建一个响应式变量
    const uploadedFont = ref(null)
    
    const handleFileChange = (file) => {
      uploadedFont.value = file
      emit('font-selected', {
        type: 'custom',
        file: file,
        name: file.name
      })
    }
    
    // 监听字体选择变化
    watch(selectedFont, (newValue) => {
      emit('font-selected', {
        type: 'preset',
        name: newValue
      })
    })
    
    return {
      selectedFont,
      uploadedFont,
      handleFileChange
    }
  }
}
</script>

<style scoped>
.font-options {
  width: 100%;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 0 0 20px 0;
  margin: 0;
  position: relative;
  z-index: 1;
  min-height: 200px;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;
}

.section-header .el-icon {
  font-size: 24px;
  color: #409EFF;
}

.font-content {
  padding: 0 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.font-selection {
  margin-bottom: 20px;
}

.font-radio-group {
  display: flex;
  justify-content: space-around;
  width: 100%;
}

.upload-section {
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.upload-section p {
  margin-bottom: 10px;
  font-size: 14px;
  color: #606266;
}

.font-uploader {
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .font-radio-group {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>