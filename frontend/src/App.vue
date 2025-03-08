<template>
  <div class="app-container">
    <el-container>
      <el-header height="70px">
        <div class="logo">
          <img src="./assets/logo.svg" alt="WordArt锦书" class="logo-img" />
          <h1>WordArt锦书 - 百家姓生成</h1>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="showHistory">
            <el-icon><Picture /></el-icon>
            历史图片
          </el-button>
        </div>
      </el-header>
      
      <el-container class="main-container">
        <!-- 左侧参数控制区 -->
        <el-aside width="400px" class="control-panel">
          <div class="control-panel-inner">
            <!-- 姓氏输入 -->
            <div class="surname-input-container">
              <h2>输入姓氏</h2>
              <el-input
                v-model="surname"
                placeholder="请输入姓氏（1-2个汉字）"
                maxlength="2"
                show-word-limit
                class="surname-input"
              />
            </div>
            
            <!-- 模式选择 -->
            <div class="mode-selector">
              <el-tabs v-model="activeMode" @tab-change="handleModeChange">
                <el-tab-pane label="预设风格" name="preset">
                  <preset-options 
                    @style-selected="handlePresetStyleSelected" 
                    :loading="loading"
                  />
                </el-tab-pane>
                <el-tab-pane label="自定义风格" name="custom">
                  <custom-options 
                    @custom-options-updated="handleCustomOptionsUpdated"
                    :loading="loading"
                  />
                </el-tab-pane>
              </el-tabs>
            </div>
            
            <!-- 生成按钮 -->
            <div class="generate-button-container">
              <el-button 
                type="primary" 
                :loading="loading" 
                @click="generateImage" 
                :disabled="!isFormValid"
                class="generate-button"
              >
                生成图片
                <el-icon class="el-icon--right"><Picture /></el-icon>
              </el-button>
              <div class="image-count-selector">
                <span>生成数量:</span>
                <el-select v-model="imageCount" :disabled="loading">
                  <el-option v-for="n in 4" :key="n" :label="n" :value="n" />
                </el-select>
              </div>
            </div>
          </div>
        </el-aside>
        
        <!-- 右侧图片展示区 -->
        <el-main class="image-display">
          <div class="image-preview-container">
            <div v-if="loading" class="loading-container">
              <el-skeleton :rows="10" animated />
            </div>
            <div v-else-if="currentImages.length === 0" class="empty-state">
              <el-empty description="尚未生成图片" />
              <p>请在左侧设置参数并点击生成按钮</p>
            </div>
            <div v-else class="image-preview">
              <img :src="currentImages[selectedImageIndex].url" alt="生成的姓氏图片" class="main-image" />
              <div class="image-info">
                <p>姓氏: {{ surname }}</p>
                <p>风格: {{ getStyleDisplayName() }}</p>
                <p>生成时间: {{ formatDate(currentImages[selectedImageIndex].createdAt) }}</p>
              </div>
            </div>
          </div>
          
          <!-- 缩略图区域 -->
          <div v-if="currentImages.length > 0" class="thumbnails-container">
            <div 
              v-for="(image, index) in currentImages" 
              :key="index"
              class="thumbnail"
              :class="{ active: selectedImageIndex === index }"
              @click="selectedImageIndex = index"
            >
              <img :src="image.url" alt="缩略图" />
            </div>
          </div>
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 历史图片对话框 -->
    <el-dialog
      v-model="historyDialogVisible"
      title="历史生成图片"
      width="80%"
      class="history-dialog"
    >
      <div v-if="historyImages.length === 0" class="empty-history">
        <el-empty description="暂无历史记录" />
      </div>
      <div v-else class="history-grid">
        <div 
          v-for="(batch, batchIndex) in groupedHistoryImages" 
          :key="batchIndex"
          class="history-batch"
        >
          <div class="batch-info">
            <h3>{{ formatDate(batch[0].createdAt) }}</h3>
            <p>姓氏: {{ batch[0].surname }}</p>
            <p>风格: {{ batch[0].styleName }}</p>
          </div>
          <div class="batch-images">
            <div 
              v-for="(image, imageIndex) in batch" 
              :key="imageIndex"
              class="history-image"
              @click="selectHistoryImage(batch, imageIndex)"
            >
              <img :src="image.url" alt="历史图片" />
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="historyDialogVisible = false">关闭</el-button>
          <el-button 
            type="primary" 
            @click="useSelectedHistoryImage" 
            :disabled="!selectedHistoryBatch"
          >
            使用选中图片
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { Picture } from '@element-plus/icons-vue'
import { ElMessage, ElLoading } from 'element-plus'
import PresetOptions from './components/PresetOptions.vue'
import CustomOptions from './components/CustomOptions.vue'

export default {
  name: 'App',
  components: {
    PresetOptions,
    CustomOptions,
    Picture
  },
  setup() {
    // 基本状态
    const surname = ref('')
    const activeMode = ref('preset')
    const loading = ref(false)
    const imageCount = ref(1)
    
    // 图片相关状态
    const currentImages = ref([])
    const historyImages = ref([])
    const selectedImageIndex = ref(0)
    const historyDialogVisible = ref(false)
    const selectedHistoryBatch = ref(null)
    const selectedHistoryImageIndex = ref(0)
    
    // 选项状态
    const presetStyle = ref('')
    const customOptions = reactive({
      prompt: '',
      refImageUrl: null,
      fontName: 'gufeng1',
      textStrength: 0.5,
      textInverse: false
    })
    
    // 计算属性
    const isFormValid = computed(() => {
      if (!surname.value || surname.value.length > 2) return false
      
      if (activeMode.value === 'preset') {
        return presetStyle.value !== ''
      } else {
        // 自定义模式下，提示词和参考图至少需要一项
        return customOptions.prompt || customOptions.refImageUrl
      }
    })
    
    // 分组历史图片
    const groupedHistoryImages = computed(() => {
      const groups = []
      let currentGroup = []
      let currentTaskId = null
      
      for (const image of historyImages.value) {
        if (image.taskId !== currentTaskId) {
          if (currentGroup.length > 0) {
            groups.push([...currentGroup])
          }
          currentGroup = [image]
          currentTaskId = image.taskId
        } else {
          currentGroup.push(image)
        }
      }
      
      if (currentGroup.length > 0) {
        groups.push(currentGroup)
      }
      
      return groups
    })
    
    // 方法
    const handleModeChange = (mode) => {
      activeMode.value = mode
    }
    
    const handlePresetStyleSelected = (style) => {
      presetStyle.value = style
    }
    
    const handleCustomOptionsUpdated = (options) => {
      Object.assign(customOptions, options)
    }
    
    const generateImage = async () => {
      if (!isFormValid.value) {
        ElMessage.warning('请完善表单信息')
        return
      }
      
      loading.value = true
      
      try {
        const payload = {
          model: "wordart-surnames",
          input: {
            surname: surname.value,
          },
          parameters: {
            n: imageCount.value
          }
        }
        
        if (activeMode.value === 'preset') {
          payload.input.style = presetStyle.value
        } else {
          payload.input.style = 'diy'
          payload.input.prompt = customOptions.prompt
          
          if (customOptions.refImageUrl) {
            payload.input.ref_image_url = customOptions.refImageUrl
          }
          
          payload.input.text = {
            font_name: customOptions.fontName,
            text_strength: customOptions.textStrength,
            text_inverse: customOptions.textInverse
          }
        }
        
        // 提交任务
        const taskResponse = await fetch('/api/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })
        
        if (!taskResponse.ok) {
          throw new Error('提交任务失败')
        }
        
        const taskData = await taskResponse.json()
        const taskId = taskData.output.task_id
        
        // 轮询任务状态
        const result = await pollTaskStatus(taskId)
        
        // 处理结果
        if (result.output.results && result.output.results.length > 0) {
          const newImages = result.output.results.map((item, index) => ({
            url: item.url,
            taskId: taskId,
            surname: surname.value,
            styleName: getStyleDisplayName(),
            createdAt: new Date()
          }))
          
          currentImages.value = newImages
          selectedImageIndex.value = 0
          
          // 添加到历史记录
          historyImages.value = [...newImages, ...historyImages.value]
          
          ElMessage.success('图片生成成功')
        } else {
          throw new Error('未获取到生成结果')
        }
      } catch (error) {
        console.error('生成图片失败:', error)
        ElMessage.error(`生成失败: ${error.message || '未知错误'}`)
      } finally {
        loading.value = false
      }
    }
    
    const pollTaskStatus = async (taskId) => {
      let attempts = 0
      const maxAttempts = 30
      const interval = 2000 // 2秒
      
      while (attempts < maxAttempts) {
        const response = await fetch(`/api/tasks/${taskId}`)
        
        if (!response.ok) {
          throw new Error('查询任务状态失败')
        }
        
        const data = await response.json()
        
        if (data.output.task_status === 'SUCCEEDED') {
          return data
        } else if (data.output.task_status === 'FAILED') {
          throw new Error(data.output.message || '任务执行失败')
        }
        
        // 等待一段时间后再次查询
        await new Promise(resolve => setTimeout(resolve, interval))
        attempts++
      }
      
      throw new Error('任务执行超时')
    }
    
    const getStyleDisplayName = () => {
      if (activeMode.value === 'preset') {
        const styleMap = {
          'fantasy_pavilion': '奇幻楼阁',
          'peerless_beauty': '绝色佳人',
          'landscape_pavilion': '山水楼阁',
          'traditional_buildings': '古风建筑',
          'green_dragon_girl': '青龙女侠',
          'cherry_blossoms': '樱花烂漫',
          'lovely_girl': '可爱少女',
          'ink_hero': '水墨少侠',
          'anime_girl': '动漫少女',
          'lake_pavilion': '水中楼阁',
          'tranquil_countryside': '宁静乡村',
          'dusk_splendor': '黄昏美景'
        }
        return styleMap[presetStyle.value] || presetStyle.value
      } else {
        return '自定义风格'
      }
    }
    
    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleString('zh-CN')
    }
    
    const showHistory = () => {
      historyDialogVisible.value = true
      selectedHistoryBatch.value = null
    }
    
    const selectHistoryImage = (batch, imageIndex) => {
      selectedHistoryBatch.value = batch
      selectedHistoryImageIndex.value = imageIndex
    }
    
    const useSelectedHistoryImage = () => {
      if (!selectedHistoryBatch.value) return
      
      const batch = selectedHistoryBatch.value
      const imageIndex = selectedHistoryImageIndex.value
      
      currentImages.value = batch
      selectedImageIndex.value = imageIndex
      historyDialogVisible.value = false
      
      // 恢复相关设置
      surname.value = batch[0].surname
      
      if (batch[0].styleName === '自定义风格') {
        activeMode.value = 'custom'
      } else {
        activeMode.value = 'preset'
        // 找到对应的预设风格值
        const styleEntries = Object.entries({
          'fantasy_pavilion': '奇幻楼阁',
          'peerless_beauty': '绝色佳人',
          'landscape_pavilion': '山水楼阁',
          'traditional_buildings': '古风建筑',
          'green_dragon_girl': '青龙女侠',
          'cherry_blossoms': '樱花烂漫',
          'lovely_girl': '可爱少女',
          'ink_hero': '水墨少侠',
          'anime_girl': '动漫少女',
          'lake_pavilion': '水中楼阁',
          'tranquil_countryside': '宁静乡村',
          'dusk_splendor': '黄昏美景'
        })
        
        for (const [key, value] of styleEntries) {
          if (value === batch[0].styleName) {
            presetStyle.value = key
            break
          }
        }
      }
    }
    
    // 加载本地存储的历史记录
    onMounted(() => {
      const savedHistory = localStorage.getItem('wordart-history')
      if (savedHistory) {
        try {
          historyImages.value = JSON.parse(savedHistory)
        } catch (e) {
          console.error('解析历史记录失败', e)
        }
      }
    })
    
    // 保存历史记录到本地存储
    const saveHistoryToLocalStorage = () => {
      localStorage.setItem('wordart-history', JSON.stringify(historyImages.value))
    }
    
    // 监听历史记录变化，保存到本地存储
    watch(historyImages, saveHistoryToLocalStorage, { deep: true })
    
    return {
      // 状态
      surname,
      activeMode,
      loading,
      imageCount,
      currentImages,
      historyImages,
      selectedImageIndex,
      historyDialogVisible,
      selectedHistoryBatch,
      selectedHistoryImageIndex,
      presetStyle,
      customOptions,
      groupedHistoryImages,
      isFormValid,
      
      // 方法
      handleModeChange,
      handlePresetStyleSelected,
      handleCustomOptionsUpdated,
      generateImage,
      getStyleDisplayName,
      formatDate,
      showHistory,
      selectHistoryImage,
      useSelectedHistoryImage
    }
  }
}
</script>

<style>
:root {
  --primary-color: #409EFF;
  --success-color: #67C23A;
  --warning-color: #E6A23C;
  --danger-color: #F56C6C;
  --info-color: #909399;
  --border-color: #EBEEF5;
  --background-color: #F5F7FA;
  --text-color: #303133;
  --text-color-secondary: #606266;
  --border-radius: 12px;
  --box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.5;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: relative;
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-img {
  height: 40px;
  width: auto;
}

.logo h1 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.main-container {
  flex: 1;
  height: calc(100vh - 70px);
}

.control-panel {
  background-color: #fff;
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  padding: 20px;
}

.control-panel-inner {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.surname-input-container {
  margin-bottom: 16px;
}

.surname-input-container h2 {
  font-size: 18px;
  margin-bottom: 12px;
  color: var(--text-color);
}

.surname-input {
  font-size: 20px;
}

.surname-input :deep(.el-input__inner) {
  height: 50px;
  font-size: 20px;
  text-align: center;
}

.mode-selector {
  flex: 1;
}

.generate-button-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
}

.generate-button {
  height: 50px;
  font-size: 18px;
  width: 100%;
}

.image-count-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.image-display {
  display: flex;
  flex-direction: column;
  padding: 20px;
  background-color: var(--background-color);
}

.image-preview-container {
  flex: 1;
  background-color: #fff;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.loading-container {
  width: 100%;
  max-width: 600px;
}

.empty-state {
  text-align: center;
  color: var(--text-color-secondary);
}

.empty-state p {
  margin-top: 16px;
}

.image-preview {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-image {
  max-width: 100%;
  max-height: 60vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.image-info {
  margin-top: 16px;
  text-align: center;
  color: var(--text-color-secondary);
}

.thumbnails-container {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.thumbnail {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.thumbnail.active {
  border-color: var(--primary-color);
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.history-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.empty-history {
  text-align: center;
  padding: 40px 0;
}

.history-grid {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.history-batch {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.batch-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.batch-info h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-color);
}

.batch-info p {
  margin: 0;
  color: var(--text-color-secondary);
}

.batch-images {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.history-image {
  width: 150px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.history-image:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.history-image.selected {
  border-color: var(--primary-color);
}

.history-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

@media (max-width: 1200px) {
  .el-aside {
    width: 350px !important;
  }
}

@media (max-width: 992px) {
  .main-container {
    flex-direction: column;
  }
  
  .el-aside {
    width: 100% !important;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }
  
  .control-panel-inner {
    max-width: 600px;
    margin: 0 auto;
  }
  
  .image-preview-container {
    margin-top: 20px;
  }
}

@media (max-width: 768px) {
  .logo h1 {
    font-size: 16px;
  }
  
  .header-actions button {
    font-size: 12px;
  }
  
  .el-header {
    padding: 0 12px;
  }
  
  .main-container {
    height: auto;
  }
  
  .thumbnail {
    width: 80px;
    height: 80px;
  }
  
  .history-image {
    width: 120px;
    height: 120px;
  }
}
</style>
