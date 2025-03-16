<template>
  <div class="app-container">
    <el-container>
      <el-header height="70px">
        <div class="logo">
          <img src="./assets/logo.svg" alt="WordArt锦书" class="logo-img" />
          <h1>WordArt锦书 - 百家姓生成</h1>
        </div>
        <div class="header-actions">
          <user-profile 
            v-if="isLoggedIn" 
            :user="currentUser" 
            @logout="handleLogout"
            @show-history="showHistory"
          />
          <el-button v-else type="primary" @click="showUserDialog">
            <el-icon><User /></el-icon>
            登录/注册
          </el-button>
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
              <!-- taps表，tap-pane表中项，tap-change改变选项卡触发函数 -->
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
                  <!-- n默认从1开始 -->
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
              <!-- 添加错误处理 -->
              <template v-if="currentImages[selectedImageIndex]?.url">
                <img 
                  :src="currentImages[selectedImageIndex].url" 
                  alt="生成的姓氏图片" 
                  class="main-image" 
                  @error="handleImageError"
                />
              </template>
              <div v-else class="image-error">
                <el-alert
                  title="图片加载失败"
                  type="error"
                  description="无法加载图片，可能是URL无效或图片不存在"
                  show-icon
                />
              </div>
              
              <div class="image-info">
                <p>姓氏: {{ surname }}</p>
                <p>风格: {{ getStyleDisplayName() }}</p>
                <p>生成时间: {{ formatDate(currentImages[selectedImageIndex]?.createdAt) }}</p>
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
              <img :src="image.url" alt="缩略图" @error="handleThumbnailError($event, index)" />
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
      <div v-else>
        <el-table
          :data="tableHistoryImages"
          style="width: 100%"
          border
          stripe
          :default-sort="{ prop: 'createdAt', order: 'descending' }"
        >
          <el-table-column
            prop="createdAt"
            label="生成时间"
            sortable
            width="180"
            :formatter="(row) => formatDate(row.createdAt)"
          />
          <el-table-column
            prop="surname"
            label="姓氏"
            width="100"
          />
          <el-table-column
            prop="styleName"
            label="风格"
            width="150"
          />
          <el-table-column
            label="预览图"
          >
            <template #default="scope">
              <div class="history-images-grid">
                <div 
                  v-for="(image, index) in scope.row.images" 
                  :key="index"
                  class="history-image-item"
                >
                  <a 
                    :href="image.url" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    class="image-link"
                    @click.prevent="openImageInNewTab(image.url)"
                  >
                    <img 
                      :src="image.url" 
                      :alt="`${image.surname}_${index+1}`"
                      class="history-thumbnail"
                    />
                  </a>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            width="120"
          >
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="downloadHistoryImages(scope.row.images)"
              >
                下载
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="historyDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 用户登录/注册对话框 -->
    <user-dialog
      v-model:visible="userDialogVisible"
      :initial-mode="userDialogMode"
      @auth-success="handleAuthSuccess"
    />
  </div>
</template>

<script>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { Picture, User } from '@element-plus/icons-vue'
import { ElMessage, ElLoading, ElMessageBox } from 'element-plus'
import PresetOptions from './components/PresetOptions.vue'
import CustomOptions from './components/CustomOptions.vue'
import { UserProfile, UserDialog } from './components/auth'
import { isAuthenticated, getCurrentUser, logout } from './utils/auth'

export default {
  name: 'App',
  components: {
    PresetOptions,
    CustomOptions,
    Picture,
    UserProfile,
    UserDialog
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
    
    // 用户相关状态
    const isLoggedIn = ref(false)
    const currentUser = ref(null)
    const userDialogVisible = ref(false)
    const userDialogMode = ref('login')
    
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
            // 当切换到新的任务时，将当前分组添加到结果中,...是扩展运算符，将currentGroup数组中的元素逐个添加到新数组中
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
    
    // 将历史图片转换为表格数据格式
    const tableHistoryImages = computed(() => {
      // 按任务ID分组
      const groupedByTaskId = {};
      historyImages.value.forEach(image => {
        if (!groupedByTaskId[image.taskId]) {
          groupedByTaskId[image.taskId] = {
            taskId: image.taskId,
            surname: image.surname,
            styleName: image.styleName,
            createdAt: image.createdAt,
            images: []
          };
        }
        groupedByTaskId[image.taskId].images.push(image);
      });
      
      // 转换为数组
      return Object.values(groupedByTaskId);
    });
    
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
          if (customOptions.prompt) {
            payload.input.prompt = customOptions.prompt
          }
          
          if (customOptions.refImageUrl) {
            payload.input.ref_image_url = customOptions.refImageUrl
          }
          
          // 确保在自定义模式下始终包含text对象
          payload.input.text = {
            font_name: customOptions.ttfUrl ? null : customOptions.fontName,
            ttf_url: customOptions.ttfUrl,
            text_strength: customOptions.textStrength,
            text_inverse: customOptions.textInverse
          }
        }
        
        // 添加认证头
        const headers = {
          'Content-Type': 'application/json'
        }
        
        // 如果用户已登录，添加认证头
        if (isLoggedIn.value) {
          headers['Authorization'] = `Bearer ${localStorage.getItem('auth_token')}`
        }
        
        console.log('提交生成请求，payload:', payload);
        
        // 提交任务
        const taskResponse = await fetch('/api/generate', {
          method: 'POST',
          headers,
          body: JSON.stringify(payload)
        })
        
        if (!taskResponse.ok) {
          const errorText = await taskResponse.text();
          console.error('提交任务失败，状态码:', taskResponse.status, '错误信息:', errorText);
          throw new Error(`提交任务失败: ${errorText || taskResponse.statusText}`);
        }
        
        const taskData = await taskResponse.json()
        console.log('任务提交成功，返回数据:', taskData);
        const taskId = taskData.output.task_id
        
        // 轮询任务状态
        console.log('开始轮询任务状态，任务ID:', taskId);
        const result = await pollTaskStatus(taskId)
        console.log('任务完成，结果:', result);
        
        // 处理结果
        if (result.output.results && result.output.results.length > 0) {
          console.log('生成的图片结果:', result.output.results);
          
          const newImages = result.output.results.map((item, index) => ({
            url: item.url,
            taskId: taskId,
            surname: surname.value,
            styleName: getStyleDisplayName(),
            createdAt: new Date()
          }))
          
          console.log('处理后的图片数据:', newImages);
          
          currentImages.value = newImages
          selectedImageIndex.value = 0
          
          console.log('当前图片数组:', currentImages.value);
          console.log('选中的图片索引:', selectedImageIndex.value);
          console.log('当前选中的图片URL:', currentImages.value[selectedImageIndex.value]?.url);
          
          // 添加到历史记录
          historyImages.value = [...newImages, ...historyImages.value]
          
          // 如果用户已登录，保存图片到服务器
          if (isLoggedIn.value) {
            saveImagesToServer(newImages)
          }
          
          ElMessage.success('图片生成成功')
        } else {
          console.error('未获取到生成结果，完整响应:', result);
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
        console.log(`轮询任务状态，第 ${attempts + 1} 次尝试`);
        const response = await fetch(`/api/tasks/${taskId}`)
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('查询任务状态失败，状态码:', response.status, '错误信息:', errorText);
          throw new Error(`查询任务状态失败: ${errorText || response.statusText}`);
        }
        
        const data = await response.json()
        console.log(`任务状态: ${data.output.task_status}`);
        
        if (data.output.task_status === 'SUCCEEDED') {
          return data
        } else if (data.output.task_status === 'FAILED') {
          console.error('任务执行失败，详细信息:', data.output);
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
    
    const showUserDialog = () => {
      userDialogVisible.value = true
      userDialogMode.value = 'login'
    }
    
    const handleAuthSuccess = (user) => {
      isLoggedIn.value = true
      currentUser.value = user
      userDialogVisible.value = false
      
      // 获取用户的图片
      fetchUserImages()
    }
    
    const handleLogout = async () => {
      try {
        // 调用后端登出接口
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        })
      } catch (error) {
        console.error('登出请求失败:', error)
      }
      
      // 无论后端请求是否成功，都清除本地状态
      logout()
      isLoggedIn.value = false
      currentUser.value = null
    }
    
    // 获取图片列表
    const fetchUserImages = async () => {
      if (!isLoggedIn.value) return
      
      try {
        const response = await fetch('/api/images', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          // 对于登录用户，完全使用服务器数据替换本地历史记录
          if (data.images && data.images.length > 0) {
            // 将服务器返回的所有图片转换为本地格式
            const serverImages = data.images.map(img => ({
              url: img.url,
              taskId: img.task_id,
              surname: img.surname,
              styleName: img.style_name,
              createdAt: new Date(img.created_at)
            }))
            
            // 完全替换本地历史记录
            historyImages.value = serverImages
            
            // 保存到本地存储
            saveHistoryToLocalStorage()
            
            console.log('从服务器加载了', serverImages.length, '张历史图片')
          }
        }
      } catch (error) {
        console.error('获取用户图片失败:', error)
      }
    }
    
    // 加载本地存储的历史记录
    onMounted(() => {
      // 检查用户登录状态
      if (isAuthenticated()) {
        isLoggedIn.value = true
        currentUser.value = getCurrentUser()
        
        // 获取用户资料
        fetchUserProfile()
        
        // 获取用户的历史图片（从服务器）
        fetchUserImages()
      } else {
        // 未登录用户才从本地存储加载历史记录
        const savedHistory = localStorage.getItem('wordart-history')
        if (savedHistory) {
          try {
            historyImages.value = JSON.parse(savedHistory)
          } catch (e) {
            console.error('解析历史记录失败', e)
          }
        }
      }
    })
    
    // 获取用户资料
    const fetchUserProfile = async () => {
      if (!isLoggedIn.value) return
      
      try {
        const response = await fetch('/api/auth/profile', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          currentUser.value = data.user
        } else if (response.status === 401) {
          // 令牌无效，登出用户
          handleLogout()
        }
      } catch (error) {
        console.error('获取用户资料失败:', error)
      }
    }
    
    // 保存历史记录到本地存储
    const saveHistoryToLocalStorage = () => {
      localStorage.setItem('wordart-history', JSON.stringify(historyImages.value))
    }
    
    // 监听历史记录变化，保存到本地存储
    watch(historyImages, saveHistoryToLocalStorage, { deep: true })
    
    // 保存图片到服务器
    const saveImagesToServer = async (images) => {
      if (!isLoggedIn.value || !images || images.length === 0) return
      
      try {
        // 构建保存图片的请求数据
        const saveData = images.map(image => ({
          task_id: image.taskId,
          url: image.url,
          surname: image.surname,
          style: activeMode.value === 'preset' ? presetStyle.value : 'diy',
          style_name: image.styleName,
          prompt: activeMode.value === 'custom' ? customOptions.prompt : null,
          ref_image_url: activeMode.value === 'custom' ? customOptions.refImageUrl : null,
          font_name: activeMode.value === 'custom' ? customOptions.fontName : null,
          text_strength: activeMode.value === 'custom' ? customOptions.textStrength : null,
          text_inverse: activeMode.value === 'custom' ? customOptions.textInverse : null
        }))
        
        // 发送保存请求
        await fetch('/api/images/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: JSON.stringify({ images: saveData })
        })
      } catch (error) {
        console.error('保存图片到服务器失败:', error)
      }
    }
    
    const handleImageError = (event) => {
      console.error('主图片加载失败:', event);
      event.target.classList.add('image-error');
      // 可以在这里设置一个默认图片
      // event.target.src = '/path/to/fallback-image.png';
    }
    
    const handleThumbnailError = (event, index) => {
      console.error(`缩略图 ${index} 加载失败:`, event);
      event.target.classList.add('thumbnail-error');
      // 可以在这里设置一个默认图片
      // event.target.src = '/path/to/fallback-thumbnail.png';
    }
    
    // 在setup函数中添加
    const isDevelopment = ref(process.env.NODE_ENV === 'development');
    
    // 添加下载历史图片的方法
    const downloadHistoryImages = async (images) => {
      if (!images || images.length === 0) return;
      
      try {
        // 如果只有一张图片，直接下载
        if (images.length === 1) {
          downloadSingleImage(images[0].url, `${images[0].surname}_${images[0].styleName}.png`);
          return;
        }
        
        // 如果有多张图片，提示用户选择下载方式
        ElMessageBox.confirm(
          `共有 ${images.length} 张图片，您想如何下载？`,
          '下载图片',
          {
            confirmButtonText: '全部下载',
            cancelButtonText: '选择一张',
            type: 'info',
          }
        )
          .then(() => {
            // 全部下载
            images.forEach((image, index) => {
              setTimeout(() => {
                downloadSingleImage(
                  image.url, 
                  `${image.surname}_${image.styleName}_${index + 1}.png`
                );
              }, index * 500); // 间隔下载，避免浏览器阻止
            });
            ElMessage.success(`开始下载 ${images.length} 张图片`);
          })
          .catch(() => {
            // 选择一张下载
            ElMessageBox.prompt(
              '请输入要下载的图片序号 (1-' + images.length + ')',
              '选择图片',
              {
                confirmButtonText: '下载',
                cancelButtonText: '取消',
                inputPattern: new RegExp(`^[1-${images.length}]$`),
                inputErrorMessage: `请输入1-${images.length}之间的数字`
              }
            )
              .then(({ value }) => {
                const index = parseInt(value) - 1;
                downloadSingleImage(
                  images[index].url, 
                  `${images[index].surname}_${images[index].styleName}.png`
                );
              })
              .catch(() => {
                // 用户取消
              });
          });
      } catch (error) {
        console.error('下载图片失败:', error);
        ElMessage.error('下载图片失败');
      }
    };
    
    // 下载单张图片
    const downloadSingleImage = (url, filename) => {
      // 创建一个隐藏的a标签
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    };
    
    // 添加在浏览器中查看图片的方法
    const viewImageInBrowser = (url) => {
      // 创建一个新的标签页
      const newTab = window.open('', '_blank');
      
      // 如果无法创建新标签页，回退到直接打开URL
      if (!newTab) {
        window.open(url, '_blank');
        return;
      }
      
      // 创建一个HTML页面，使用iframe显示图片
      newTab.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>图片查看器</title>
          <style>
            body, html {
              margin: 0;
              padding: 0;
              height: 100%;
              width: 100%;
              overflow: hidden;
              background-color: #1e1e1e;
              display: flex;
              justify-content: center;
              align-items: center;
            }
            img {
              max-width: 100%;
              max-height: 100%;
              object-fit: contain;
            }
            .toolbar {
              position: fixed;
              top: 10px;
              right: 10px;
              background-color: rgba(0, 0, 0, 0.5);
              border-radius: 5px;
              padding: 5px;
            }
            .toolbar button {
              background-color: #4CAF50;
              border: none;
              color: white;
              padding: 5px 10px;
              text-align: center;
              text-decoration: none;
              display: inline-block;
              font-size: 14px;
              margin: 2px;
              cursor: pointer;
              border-radius: 3px;
            }
          </style>
        </head>
        <body>
          <img src="${url}" alt="图片查看" />
          <div class="toolbar">
            <button onclick="window.location.href='${url}'">下载</button>
          </div>
        </body>
        </html>
      `);
      newTab.document.close();
    };
    
    // 添加点击图片在新标签页打开的功能
    const openImageInNewTab = (url) => {
      viewImageInBrowser(url);
    };
    
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
      isLoggedIn,
      currentUser,
      userDialogVisible,
      userDialogMode,
      tableHistoryImages,
      
      // 方法
      handleModeChange,
      handlePresetStyleSelected,
      handleCustomOptionsUpdated,
      generateImage,
      getStyleDisplayName,
      formatDate,
      showHistory,
      selectHistoryImage,
      showUserDialog,
      handleAuthSuccess,
      handleLogout,
      fetchUserProfile,
      fetchUserImages,
      saveImagesToServer,
      handleImageError,
      handleThumbnailError,
      downloadHistoryImages,
      downloadSingleImage,
      viewImageInBrowser,
      openImageInNewTab,
      
      // 计算属性
      isDevelopment
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

/* 历史图片表格样式 */
.history-images-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-start;
}

.history-image-item {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
}

.history-image-item:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.history-image-item:hover::after {
  content: '点击查看';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 12px;
  padding: 2px 0;
  text-align: center;
}

.history-thumbnail {
  width: 80px;
  height: 80px;
  object-fit: cover;
  display: block;
}

.image-link {
  display: block;
  width: 100%;
  height: 100%;
  text-decoration: none;
}

/* 表格样式优化 */
.el-table {
  --el-table-border-color: var(--border-color);
  --el-table-header-bg-color: var(--background-color);
}

.el-table th {
  font-weight: 600;
  color: var(--text-color);
}

.el-table .el-button {
  margin: 0;
}

/* 调试信息样式 */
.debug-info {
  background-color: #f8f8f8;
  border: 1px dashed #ccc;
  padding: 10px;
  margin-bottom: 15px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

.debug-info p {
  margin: 5px 0;
}

/* 图片错误状态 */
.image-error {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  width: 100%;
  max-width: 600px;
}

img.image-error {
  border: 2px solid var(--danger-color);
  opacity: 0.6;
}

img.thumbnail-error {
  border: 2px solid var(--danger-color);
  opacity: 0.6;
}
</style>
