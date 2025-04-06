<template>
    <div class="app-container other-page">
      <el-container>
        <el-header height="70px">
          <div class="logo">
            <img src="../assets/logo.svg" alt="WordArt锦书" class="logo-img" />
            <h1>WordArt锦书 - 百家姓生成</h1>
          </div>
          <div class="header-actions">
            <user-profile 
              v-if="isLoggedIn" 
              :user="currentUser" 
              @logout="handleLogout"
              @show-history="showHistory"
            />
            <el-button v-else type="primary" @click="showUserDialog" class="rounded-button">
              <el-icon><User /></el-icon>
              登录/注册
            </el-button>
            <el-button type="primary" @click="showHistory" class="rounded-button">
              <el-icon><Picture /></el-icon>
              历史图片
            </el-button>
          </div>
        </el-header>
        
        <el-container class="main-container">
          <!-- 左侧参数控制区 -->
          <div class="control-panel">
            <el-card class="control-panel-card">
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
            </el-card>
          </div>
          
          <!-- 右侧图片展示区 -->
          <div class="image-display">
            <el-card class="image-display-card">
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
            </el-card>
          </div>
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
          
          <!-- 添加分页组件 -->
          <div class="pagination-container">
            <div class="custom-pagination">
              <button 
                class="page-arrow page-prev" 
                :class="{ disabled: currentPage <= 1 }"
                @click="handlePrevPage"
                :disabled="currentPage <= 1"
                title="上一页"
              >
                <i class="el-icon">
                  <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                    <path fill="currentColor" d="M609.408 149.376 277.76 489.6a32 32 0 0 0 0 44.672l331.648 340.352a29.12 29.12 0 0 0 41.728 0 30.592 30.592 0 0 0 0-42.752L339.264 511.936l311.872-319.872a30.592 30.592 0 0 0 0-42.688 29.12 29.12 0 0 0-41.728 0z"></path>
                  </svg>
                </i>
              </button>
              <span class="page-info">第 {{ currentPage }} 页 / 共 {{ totalPages || 1 }} 页</span>
              <button 
                class="page-arrow page-next" 
                :class="{ disabled: currentPage >= totalPages }"
                @click="handleNextPage"
                :disabled="currentPage >= totalPages"
                title="下一页"
              >
                <i class="el-icon">
                  <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                    <path fill="currentColor" d="M340.864 149.312a30.592 30.592 0 0 0 0 42.752L652.736 512 340.864 831.872a30.592 30.592 0 0 0 0 42.752 29.12 29.12 0 0 0 41.728 0L714.24 534.336a32 32 0 0 0 0-44.672L382.592 149.376a29.12 29.12 0 0 0-41.728 0z"></path>
                  </svg>
                </i>
              </button>
            </div>
          </div>
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
  import PresetOptions from '../components/wordart/PresetOptions.vue'
  import CustomOptions from '../components/wordart/CustomOptions.vue'
  import { UserProfile, UserDialog } from '../components/auth'
  import { isAuthenticated, getCurrentUser, logout } from '../utils/auth'
  
  export default {
    name: 'WordArtView',
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
      const allHistoryImages = ref([])
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
      
      // 分页相关状态
      const currentPage = ref(1)
      const pageSize = ref(5) // 固定每页显示5项
      const totalImages = ref(0) // 图片分组后的总数
      const totalPages = computed(() => Math.ceil(totalImages.value / pageSize.value) || 1) // 确保至少有1页
      
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
        console.log('重新计算表格数据...')
        // 先进行任务ID分组
        const groupedByTaskId = {}
        
        // 使用已经排序好的historyImages (所有图片)
        historyImages.value.forEach(image => {
          if (!groupedByTaskId[image.taskId]) {
            groupedByTaskId[image.taskId] = {
              taskId: image.taskId,
              surname: image.surname,
              styleName: image.styleName,
              createdAt: image.createdAt,
              images: []
            }
          }
          groupedByTaskId[image.taskId].images.push(image)
        })
        
        // 转换为数组（已经排好序了）
        const allGroups = Object.values(groupedByTaskId)
        
        // 打印调试信息
        console.log(`分组后的总数据项: ${allGroups.length}，当前页: ${currentPage.value}，每页数量: ${pageSize.value}`)
        
        // 计算分页
        const startIndex = (currentPage.value - 1) * pageSize.value
        const endIndex = Math.min(startIndex + pageSize.value, allGroups.length)
        
        // 获取当前页的数据
        const currentPageData = allGroups.slice(startIndex, endIndex)
        
        console.log(`当前页数据: 从${startIndex}到${endIndex}，共${currentPageData.length}条`)
        
        return currentPageData
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
            allHistoryImages.value = [...newImages, ...allHistoryImages.value]
            historyImages.value = [...newImages, ...historyImages.value]
            
            // 如果用户已登录，保存图片到服务器
            if (isLoggedIn.value) {
              saveImagesToServer(newImages)
            }
            
            // 如果历史对话框是打开的，确保分页状态正确
            if (historyDialogVisible.value) {
              // 若添加了新内容，自动跳到第一页以显示最新内容
              currentPage.value = 1
              
              // 更新总任务数量
              updateTotalImagesCount()
              
              console.log(`生成新图片后，总页数: ${totalPages.value}`)
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
        // 每次打开历史对话框，重置为第一页
        currentPage.value = 1
        
        // 触发重新计算总数
        if (isLoggedIn.value) {
          // 如果是登录用户，重新获取所有历史图片
          fetchAllUserImages()
        } else {
          // 如果是未登录用户，使用本地数据
          updateTotalImagesCount()
        }
        
        console.log(`显示历史对话框，总页数: ${totalPages.value}`)
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
        fetchAllUserImages()
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
      
      // 获取所有历史图片（不分页）
      const fetchAllUserImages = async () => {
        if (!isLoggedIn.value) return
        
        try {
          console.log('获取所有历史图片...')
          // 请求所有图片，使用一个很大的页面大小
          const response = await fetch(`/api/images?page=1&per_page=1000`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            }
          })
          
          if (response.ok) {
            const data = await response.json()
            console.log('获取到历史图片数据:', data)
            
            if (data.images && data.images.length > 0) {
              // 将服务器返回的所有图片转换为本地格式
              const serverImages = data.images.map(img => ({
                url: img.url,
                taskId: img.task_id,
                surname: img.surname,
                styleName: img.style_name,
                createdAt: new Date(img.created_at)
              }))
              
              // 存储所有图片
              allHistoryImages.value = serverImages
              
              // 根据分页设置当前页显示的图片
              updateCurrentPageImages()
              
              // 手动计算总任务数
              updateTotalImagesCount()
              
              // 保存到本地存储
              saveHistoryToLocalStorage()
              
              console.log(`从服务器加载了 ${serverImages.length} 张图片，分组后有 ${totalImages.value} 个任务，共 ${totalPages.value} 页`)
            } else {
              console.log('服务器返回的图片数据为空')
              allHistoryImages.value = []
              historyImages.value = []
              totalImages.value = 0
            }
          } else {
            console.error('获取历史图片失败，状态码:', response.status)
          }
        } catch (error) {
          console.error('获取所有历史图片失败:', error)
        }
      }
      
      // 更新当前页显示的图片
      const updateCurrentPageImages = () => {
        // 检查是否有图片，没有则直接返回
        if (allHistoryImages.value.length === 0) {
          historyImages.value = []
          return
        }
        
        // 按创建时间排序（最新的在前面）
        const sorted = [...allHistoryImages.value].sort((a, b) => 
          new Date(b.createdAt) - new Date(a.createdAt)
        )
        
        // 设置当前历史图片
        historyImages.value = sorted
        
        console.log(`更新当前页面数据完成，共 ${historyImages.value.length} 张图片`)
      }
      
      // 更新总任务数
      const updateTotalImagesCount = () => {
        // 计算唯一任务ID的数量
        const uniqueTaskIds = new Set()
        historyImages.value.forEach(img => uniqueTaskIds.add(img.taskId))
        totalImages.value = uniqueTaskIds.size
        
        console.log(`计算出唯一任务ID数量: ${uniqueTaskIds.size}, 总页数: ${totalPages.value}`)
      }
      
      // 获取图片列表
      const fetchUserImages = async () => {
        if (!isLoggedIn.value) return
        
        try {
          const response = await fetch(`/api/images?page=${currentPage.value}&per_page=${pageSize.value}`, {
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
              
              // 更新总数
              if (data.total) {
                totalImages.value = data.total
              }
              
              // 保存到本地存储
              saveHistoryToLocalStorage()
              
              console.log('从服务器加载了', serverImages.length, '张历史图片, 总数:', data.total)
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
          fetchAllUserImages()
        } else {
          // 未登录用户才从本地存储加载历史记录
          const savedHistory = localStorage.getItem('wordart-history')
          if (savedHistory) {
            try {
              allHistoryImages.value = JSON.parse(savedHistory)
              historyImages.value = allHistoryImages.value
              // 手动计算总任务数
              updateTotalImagesCount()
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
        localStorage.setItem('wordart-history', JSON.stringify(allHistoryImages.value))
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
      
      // 简化分页处理方法
      const handlePrevPage = () => {
        if (currentPage.value > 1) {
          currentPage.value -= 1
          console.log(`切换到上一页: ${currentPage.value}`)
        }
      }
      
      const handleNextPage = () => {
        if (currentPage.value < totalPages.value) {
          currentPage.value += 1
          console.log(`切换到下一页: ${currentPage.value}`)
        }
      }
      
      return {
        // 状态
        surname,
        activeMode,
        loading,
        imageCount,
        currentImages,
        historyImages,
        allHistoryImages,
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
        // 分页相关
        currentPage,
        pageSize,
        totalImages,
        totalPages,
        
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
        fetchAllUserImages,
        updateCurrentPageImages,
        updateTotalImagesCount,
        saveImagesToServer,
        handleImageError,
        handleThumbnailError,
        downloadHistoryImages,
        downloadSingleImage,
        viewImageInBrowser,
        openImageInNewTab,
        // 分页方法
        handlePrevPage,
        handleNextPage,
        
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
    padding: 20px;
    background-color: var(--background-color);
    display: flex;
  }
  
  .control-panel {
    width: 400px;
    padding-right: 15px;
  }
  
  .control-panel-card {
    height: 100%;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }
  
  .control-panel-inner {
    display: flex;
    flex-direction: column;
    gap: 24px;
    padding: 20px;
    height: 100%;
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
    flex: 1;
    padding-left: 15px;
  }
  
  .image-display-card {
    height: 100%;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
  }
  
  .image-preview-container {
    flex: 1;
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
    margin: 0 20px 20px;
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
    .control-panel {
      width: 350px;
    }
  }
  
  @media (max-width: 992px) {
    .main-container {
      flex-direction: column;
      height: auto;
    }
    
    .control-panel {
      width: 100%;
      padding-right: 0;
      margin-bottom: 20px;
    }
    
    .image-display {
      padding-left: 0;
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
  
  /* 添加分页容器样式 */
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
  
  /* 自定义分页样式 */
  .custom-pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: white;
    border-radius: 25px;
    padding: 8px 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }
  
  .custom-pagination:hover {
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
  
  .page-arrow {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border: none;
    background-color: #f5f7fa;
    color: #606266;
    transition: all 0.3s ease;
    margin: 0 10px;
    position: relative;
    overflow: hidden;
  }
  
  .page-arrow::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, rgba(64, 158, 255, 0.2) 0%, rgba(64, 158, 255, 0) 70%);
    transform: scale(0);
    transition: transform 0.4s ease;
  }
  
  .page-arrow:hover::before {
    transform: scale(2);
  }
  
  .page-arrow:hover {
    background-color: var(--primary-color);
    color: white;
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(64, 158, 255, 0.4);
  }
  
  .page-arrow:active {
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
  }
  
  .page-arrow.disabled {
    background-color: #f5f7fa;
    color: #c0c4cc;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
  }
  
  .page-arrow.disabled:hover::before {
    transform: scale(0);
  }
  
  .page-info {
    margin: 0 16px;
    font-size: 15px;
    font-weight: 500;
    color: #606266;
    min-width: 120px;
    text-align: center;
  }
  
  .header-actions .rounded-button {
    border-radius: 20px;
    padding: 8px 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }
  
  .header-actions .rounded-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
  }
  </style>
  