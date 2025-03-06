<!--
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-05 22:52:14
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-06 20:46:14
 * @FilePath: \WebArt\frontend\src\App.vue
 * @Description: 
 * 
 * Copyright (c) 2025 by Furdow, All Rights Reserved. 
-->
<template>
  <div class="app-container">
    <header class="header">
      <div class="logo">
        <el-icon><Palette /></el-icon>
        <span>WebArt</span>
      </div>
    </header>
    
    <main class="main">
      <div class="content-container animate__animated animate__fadeIn">
        <h1>创意百家姓</h1>
        <p class="subtitle">选择预设或自定义您的艺术风格</p>
        
        <!-- 模式选择区 -->
        <el-radio-group v-model="mode" class="mode-selector" @change="handleModeChange">
          <el-radio-button label="preset">预设模式</el-radio-button>
          <el-radio-button label="custom">自定义模式</el-radio-button>
        </el-radio-group>
        
        <!-- 姓氏输入区 -->
        <el-input 
          v-model="surname"
          placeholder="请输入姓氏（最多支持3个字）"
          maxlength="3"
          show-word-limit
          class="surname-input"
        ></el-input>
        
        <!-- 字体选择区 -->
        <div class="section-container">
          <font-options @font-selected="handleFontSelected" class="font-options-component" />
        </div>
        
        <!-- 动态组件区 -->
        <div class="section-container options-section">
          <component 
            :is="mode === 'preset' ? 'preset-options' : 'custom-options'"
            @option-selected="handlePresetSelected"
            @custom-applied="handleCustomApplied"
            class="options-component"
          ></component>
        </div>
        
        <!-- 生成按钮 -->
        <div class="button-container">
          <el-button 
            type="primary" 
            @click="generateArt"
            :loading="loading"
            class="generate-button"
          >生成创意百家姓
            <el-icon class="el-icon--right"><Magic /></el-icon>
          </el-button>
        </div>

        <!-- 预览区域 -->
        <div class="preview-section" :class="{ 'has-content': generatedImage || selectedStyle }">
          <div v-if="generatedImage" class="image-preview">
            <img :src="generatedImage" alt="生成的百家姓图片" />
          </div>
          <div v-else-if="selectedStyle" class="style-preview">
            <p>已选风格: {{ selectedStyle }}</p>
            <p v-if="selectedFont">已选字体: {{ selectedFont.name }}</p>
          </div>
          <div v-else class="empty-preview">
            <el-icon><Picture /></el-icon>
            <p>生成的图片将显示在这里</p>
          </div>
        </div>
      </div>
    </main>

    <footer class="footer">
      <p>© 2025 WebArt. All rights reserved.</p>
    </footer>
  </div>
</template>

<script>
import { ref } from 'vue'
import { Brush as Palette, MagicStick as Magic, Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PresetOptions from './PresetOptions.vue'
import CustomOptions from './CustomOptions.vue'
import FontOptions from './FontOptions.vue'
import 'element-plus/dist/index.css'
import 'animate.css'

export default {
  name: 'App',
  components: {
    PresetOptions,
    CustomOptions,
    FontOptions,
    Palette,
    Magic,
    Picture
  },
  setup() {
    const selectedStyle = ref(null)
    const selectedFont = ref(null)
    const mode = ref('preset')
    const surname = ref('')
    const loading = ref(false)
    const generatedImage = ref(null)

    const handleModeChange = () => {
      selectedStyle.value = null
    }

    const handlePresetSelected = (option) => {
      selectedStyle.value = option.name
    }

    const handleCustomApplied = (customStyle) => {
      selectedStyle.value = `自定义: ${customStyle.style}`
    }
    
    const handleFontSelected = (font) => {
      selectedFont.value = font
    }

    const generateArt = () => {
      if (!surname.value) {
        // 提示用户输入姓氏
        ElMessage.warning('请先输入姓氏')
        return
      }
      
      if (!selectedStyle.value) {
        ElMessage.warning('请选择一种风格')
        return
      }
      
      loading.value = true
      // TODO: 调用API生成图片
      console.log('生成艺术图片:', {
        surname: surname.value,
        style: selectedStyle.value,
        font: selectedFont.value ? selectedFont.value.name : '默认'
      })
      
      // 模拟API调用
      setTimeout(() => {
        // 这里应该是从API获取图片URL
        generatedImage.value = 'https://via.placeholder.com/400x200?text=' + surname.value
        loading.value = false
      }, 2000)
    }

    return {
      selectedStyle,
      selectedFont,
      mode,
      surname,
      loading,
      generatedImage,
      handleModeChange,
      handlePresetSelected,
      handleCustomApplied,
      handleFontSelected,
      generateArt
    }
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 64px;
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 1000;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.logo .el-icon {
  font-size: 32px;
}

.main {
  flex: 1;
  padding: 84px 20px 20px;
  display: flex;
  justify-content: center;
}

.content-container {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

h1 {
  font-size: 36px;
  color: #2c3e50;
  margin-bottom: 0;
}

.subtitle {
  font-size: 18px;
  color: #5c6b7f;
  margin-bottom: 0;
}

.mode-selector {
  margin-bottom: 0;
}

.surname-input {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
}

.section-container {
  width: 100%;
  margin: 0;
  position: relative;
}

.options-section {
  min-height: 450px;
}

.font-options-component,
.options-component {
  width: 100%;
}

.button-container {
  width: 100%;
  display: flex;
  justify-content: center;
  margin: 0;
}

.generate-button {
  width: 100%;
  max-width: 480px;
  height: 56px;
  font-size: 18px;
  border-radius: 28px;
}

.preview-section {
  margin: 0;
  padding: 32px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  min-height: 250px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-section.has-content {
  background: white;
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.image-preview img {
  max-width: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.style-preview {
  text-align: center;
  padding: 20px;
}

.style-preview p {
  font-size: 18px;
  color: #2c3e50;
  margin: 8px 0;
}

.empty-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.empty-preview .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-preview p {
  font-size: 16px;
}

.footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  padding: 24px;
  font-size: 16px;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .header {
    padding: 0 20px;
  }
  
  .content-container {
    padding: 10px;
    gap: 32px;
  }
  
  h1 {
    font-size: 28px;
  }
  
  .subtitle {
    font-size: 16px;
  }
  
  .preview-section {
    padding: 20px;
    min-height: 200px;
  }
  
  .options-section {
    min-height: 400px;
  }
}
</style>