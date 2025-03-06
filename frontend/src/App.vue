<template>
  <el-container class="app-container">
    <el-header class="header">
      <div class="logo">
        <el-icon><Palette /></el-icon>
        <span>WebArt</span>
      </div>
    </el-header>
    
    <el-main class="main">
      <div class="content-container animate__animated animate__fadeIn">
        <h1>Create Your Digital Art</h1>
        <p class="subtitle">Choose from presets or customize your own artistic style</p>
        
        <el-row :gutter="20" class="options-container">
          <el-col :span="12">
            <preset-options @option-selected="handlePresetSelected" />
          </el-col>
          <el-col :span="12">
            <custom-options @custom-applied="handleCustomApplied" />
          </el-col>
        </el-row>

        <div v-if="selectedStyle" class="preview-section">
          <h2>Preview</h2>
          <div class="style-preview">
            <p>Selected Style: {{ selectedStyle }}</p>
            <el-button type="primary" size="large" @click="generateArt">
              Generate Art
              <el-icon class="el-icon--right"><Magic /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </el-main>

    <el-footer class="footer">
      <p>© 2025 WebArt. All rights reserved.</p>
    </el-footer>
  </el-container>
</template>

<script>
import { ref } from 'vue'
import { Palette, Magic } from '@element-plus/icons-vue'
import PresetOptions from './PresetOptions.vue'
import CustomOptions from './CustomOptions.vue'
import 'element-plus/dist/index.css'
import 'animate.css'

export default {
  name: 'App',
  components: {
    PresetOptions,
    CustomOptions,
    Palette,
    Magic
  },
  setup() {
    const selectedStyle = ref(null)

    const handlePresetSelected = (option) => {
      selectedStyle.value = option.name
    }

    const handleCustomApplied = (customStyle) => {
      selectedStyle.value = `Custom: ${customStyle.style}`
    }

    const generateArt = () => {
      // TODO: Implement art generation
      console.log('Generating art with style:', selectedStyle.value)
    }

    return {
      selectedStyle,
      handlePresetSelected,
      handleCustomApplied,
      generateArt
    }
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.header {
  background: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.main {
  padding: 40px 20px;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

h1 {
  font-size: 48px;
  color: #2c3e50;
  margin-bottom: 20px;
}

.subtitle {
  font-size: 20px;
  color: #5c6b7f;
  margin-bottom: 40px;
}

.options-container {
  margin-top: 40px;
}

.preview-section {
  margin-top: 60px;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.style-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  padding: 20px;
}
</style> 