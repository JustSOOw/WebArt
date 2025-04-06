<template>
  <div class="app-container other-page">
    <el-container>
      <el-header height="70px">
        <div class="logo">
          <img src="../assets/logo.svg" alt="WordArt锦书" class="logo-img" />
          <h1>WordArt锦书 - AI视频生成</h1>
        </div>
        <div class="header-actions">
          <user-profile 
            v-if="isLoggedIn" 
            :user="currentUser" 
            @logout="handleLogout"
          />
          <el-button v-else type="primary" @click="showUserDialog" class="login-button rounded-button">
            <el-icon><User /></el-icon>
            登录/注册
          </el-button>
          <el-button 
            type="primary" 
            @click="openHistoryDialog" 
            class="rounded-button"
          >
            <el-icon><Histogram /></el-icon>
            历史视频
          </el-button>
        </div>
      </el-header>
      
      <el-container class="main-container">
        <!-- 左侧功能选择区 -->
        <div class="control-panel">
          <el-card class="control-panel-card">
            <div class="control-panel-inner">
              <h2 class="panel-title">创建模型</h2>
              
              <!-- 功能选择按钮 -->
              <div class="feature-buttons">
                <div class="button-row">
                  <div class="button-group">
                    <el-button 
                      :type="activeFeature === 'text-to-video' ? 'primary' : 'default'" 
                      class="feature-btn"
                      :class="{'active-btn': activeFeature === 'text-to-video'}"
                      @click="handleFeatureSelect('text-to-video')"
                    >
                      <span class="feature-btn-text">文生视频</span>
                      <el-button 
                        v-if="activeFeature === 'text-to-video'" 
                        class="model-select-btn" 
                        @click.stop="showTextModelSelect = !showTextModelSelect"
                      >
                        <el-icon><ArrowRight /></el-icon>
                      </el-button>
                    </el-button>
                  </div>
                  
                  <div class="button-group">
                    <el-button 
                      :type="activeFeature === 'image-to-video' ? 'primary' : 'default'" 
                      class="feature-btn"
                      :class="{'active-btn': activeFeature === 'image-to-video'}"
                      @click="handleFeatureSelect('image-to-video')"
                    >
                      <span class="feature-btn-text">图生视频</span>
                      <el-button 
                        v-if="activeFeature === 'image-to-video'" 
                        class="model-select-btn" 
                        @click.stop="showImageModelSelect = !showImageModelSelect"
                      >
                        <el-icon><ArrowRight /></el-icon>
                      </el-button>
                    </el-button>
                  </div>
                </div>
              </div>
              
              <!-- 文生视频模型选择卡片 -->
              <el-card v-if="showTextModelSelect && activeFeature === 'text-to-video'" class="model-select-card">
                <div class="model-options">
                  <h3>选择模型</h3>
                  
                  <el-radio-group v-model="selectedTextModel" class="model-radio-group" @change="handleTextModelChange">
                    <el-radio label="wanx2.1-t2v-turbo" class="model-radio">
                      <div class="model-info">
                        <span class="model-name">文生视频 2.1 极速</span>
                        <el-tag size="small" type="success">速度优先</el-tag>
                        <el-tooltip 
                          content="生成速度更快，表现均衡，支持480P和720P档位" 
                          placement="top"
                          class="model-desc-tooltip"
                        >
                          <el-icon class="info-icon"><QuestionFilled /></el-icon>
                        </el-tooltip>
                      </div>
                    </el-radio>
                    
                    <el-radio label="wanx2.1-t2v-plus" class="model-radio" border>
                      <div class="model-info">
                        <span class="model-name">文生视频 2.1 专业</span>
                        <el-tag size="small" type="warning">质量优先</el-tag>
                        <el-tooltip 
                          content="生成细节更丰富，画面更具质感，仅支持720P档位" 
                          placement="top"
                          class="model-desc-tooltip"
                        >
                          <el-icon class="info-icon"><QuestionFilled /></el-icon>
                        </el-tooltip>
                      </div>
                    </el-radio>
                  </el-radio-group>
                </div>
              </el-card>
              
              <!-- 图生视频模型选择卡片 -->
              <el-card v-if="showImageModelSelect && activeFeature === 'image-to-video'" class="model-select-card">
                <div class="model-options">
                  <h3>选择模型</h3>
                  
                  <el-radio-group v-model="selectedImageModel" class="model-radio-group" @change="handleImageModelChange">
                    <el-radio label="wanx2.1-i2v-turbo" class="model-radio">
                      <div class="model-info">
                        <span class="model-name">图生视频 2.1 极速</span>
                        <el-tag size="small" type="success">速度优先</el-tag>
                        <el-tooltip 
                          content="生成速度更快，支持480P和720P档位，视频时长3-5秒可选" 
                          placement="top"
                          class="model-desc-tooltip"
                        >
                          <el-icon class="info-icon"><QuestionFilled /></el-icon>
                        </el-tooltip>
                      </div>
                    </el-radio>
                    
                    <el-radio label="wanx2.1-i2v-plus" class="model-radio">
                      <div class="model-info">
                        <span class="model-name">图生视频 2.1 专业</span>
                        <el-tag size="small" type="warning">质量优先</el-tag>
                        <el-tooltip 
                          content="生成细节更丰富，画面更具质感，仅支持720P档位，固定5秒时长" 
                          placement="top"
                          class="model-desc-tooltip"
                        >
                          <el-icon class="info-icon"><QuestionFilled /></el-icon>
                        </el-tooltip>
                      </div>
                    </el-radio>
                  </el-radio-group>
                </div>
              </el-card>
              
              <!-- 提示词输入区域 -->
              <div class="input-section">
                <div v-if="activeFeature === 'text-to-video'">
                  <h3 class="input-title">提示词</h3>
                  <el-input
                    v-model="promptText"
                    type="textarea"
                    :rows="5"
                    placeholder="试试输入你的想法，尽量描述具体，可以尝试用一些风格修饰词描述你想要的视频"
                    resize="none"
                    class="prompt-input"
                    maxlength="800"
                    show-word-limit
                  />
                </div>
                
                <div v-else-if="activeFeature === 'image-to-video'">
                  <h3 class="input-title">上传图片</h3>
                  <el-upload
                    class="image-uploader"
                    action="#"
                    :auto-upload="false"
                    :show-file-list="false"
                    :on-change="handleImageChange"
                  >
                    <div v-if="imageUrl" class="image-preview">
                      <img :src="imageUrl" class="uploaded-image" />
                    </div>
                    <div v-else class="upload-placeholder">
                      <el-icon><Plus /></el-icon>
                      <div class="upload-text">点击或拖拽图片至此区域上传</div>
                      <div class="upload-hint">支持JPG/PNG/WEBP格式，大小不超过10MB</div>
                    </div>
                  </el-upload>
                  
                  <h3 class="input-title">提示词</h3>
                  <el-input
                    v-model="imagePromptText"
                    type="textarea"
                    :rows="3"
                    placeholder="输入与图片相关的提示词，帮助生成更好的视频"
                    resize="none"
                    class="prompt-input"
                    maxlength="800"
                    show-word-limit
                  />
                </div>
              </div>
              
              <!-- 文生视频分辨率和比例选择 -->
              <div v-if="activeFeature === 'text-to-video'" class="resolution-section">
                <h3 class="input-title">分辨率</h3>
                <div class="resolution-selector">
                  <el-radio-group v-model="selectedResolution" class="resolution-radios">
                    <el-radio 
                      label="720P" 
                      border 
                      :disabled="false"
                    >
                      720P
                    </el-radio>
                    <el-radio 
                      label="480P" 
                      border 
                      :disabled="selectedTextModel === 'wanx2.1-t2v-plus'"
                    >
                      480P
                    </el-radio>
                  </el-radio-group>
                </div>
                
                <h3 class="input-title">比例</h3>
                <div class="ratio-buttons">
                  <el-button 
                    :class="{'ratio-btn-active': selectedRatio === '16:9'}" 
                    @click="selectedRatio = '16:9'"
                    class="ratio-btn"
                  >
                    16:9
                  </el-button>
                  <el-button 
                    :class="{'ratio-btn-active': selectedRatio === '9:16'}" 
                    @click="selectedRatio = '9:16'"
                    class="ratio-btn"
                  >
                    9:16
                  </el-button>
                  <el-button 
                    :class="{'ratio-btn-active': selectedRatio === '1:1'}" 
                    @click="selectedRatio = '1:1'"
                    class="ratio-btn"
                  >
                    1:1
                  </el-button>
                  <el-button 
                    v-if="selectedResolution === '720P'"
                    :class="{'ratio-btn-active': selectedRatio === '4:3'}" 
                    @click="selectedRatio = '4:3'"
                    class="ratio-btn"
                  >
                    4:3
                  </el-button>
                  <el-button 
                    v-if="selectedResolution === '720P'"
                    :class="{'ratio-btn-active': selectedRatio === '3:4'}" 
                    @click="selectedRatio = '3:4'"
                    class="ratio-btn"
                  >
                    3:4
                  </el-button>
                </div>
              </div>
              
              <!-- 图生视频分辨率选择 -->
              <div v-if="activeFeature === 'image-to-video'" class="resolution-section">
                <h3 class="input-title">分辨率</h3>
                <div class="resolution-selector">
                  <el-radio-group v-model="imageResolution" class="resolution-radios">
                    <el-radio 
                      label="720P" 
                      border 
                      :disabled="false"
                    >
                      720P
                    </el-radio>
                    <el-radio 
                      label="480P" 
                      border 
                      :disabled="selectedImageModel === 'wanx2.1-i2v-plus'"
                    >
                      480P
                    </el-radio>
                  </el-radio-group>
                </div>
                
                <!-- 图生视频时长选择 (仅对turbo模型有效) -->
                <div v-if="selectedImageModel === 'wanx2.1-i2v-turbo'" class="duration-section">
                  <h3 class="input-title">视频时长 (秒)</h3>
                  <div class="duration-slider">
                    <el-slider 
                      v-model="videoDuration" 
                      :min="3" 
                      :max="5" 
                      :step="1" 
                      :marks="{3: '3秒', 4: '4秒', 5: '5秒'}"
                      show-stops
                    />
                  </div>
                </div>
              </div>
              
              <!-- 随机种子设置 -->
              <div class="seed-section">
                <h3 class="input-title">随机种子 (可选)</h3>
                <el-input 
                  v-model="seedValue" 
                  placeholder="设置随机种子，保持空白则由系统自动生成" 
                  type="number" 
                  :min="0" 
                  :max="2147483647"
                  class="seed-input"
                >
                  <template #append>
                    <el-button @click="generateRandomSeed">
                      <el-icon><RefreshRight /></el-icon>
                    </el-button>
                  </template>
                </el-input>
                <div class="seed-hint">设置相同的种子值可以生成相近的结果</div>
              </div>
              
              <!-- 智能改写开关 -->
              <div class="option-switches">
                <div class="switch-item">
                  <div class="switch-label">
                    <span>智能改写</span>
                    <el-tooltip 
                      content="开启后使用大模型对输入提示词进行智能改写，对短提示词效果提升明显，但会增加处理时间" 
                      placement="top"
                    >
                      <el-icon class="info-icon"><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </div>
                  <el-switch v-model="promptExtend" />
                </div>
              </div>
              
              <!-- 生成按钮 -->
              <div class="generate-button-container">
                <el-button 
                  type="primary" 
                  :loading="loading" 
                  @click="generateVideo" 
                  :disabled="!isFormValid"
                  class="generate-button"
                >
                  生成视频
                  <span class="credits">10</span>
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 右侧视频展示区 -->
        <div class="video-display">
          <el-card class="video-display-card">
            <div v-if="loading" class="loading-container">
              <div class="loading-content">
                <el-progress 
                  type="circle" 
                  :percentage="loadingProgress" 
                  :status="loadingStatus"
                  :stroke-width="8"
                ></el-progress>
                <div class="loading-text">{{ loadingText }}</div>
                <div class="loading-tip">视频生成需要数分钟，请耐心等待</div>
                <div v-if="taskId && showCheckStatusButton" class="loading-actions">
                  <el-button @click="checkTaskStatus" size="small">检查状态</el-button>
                </div>
              </div>
            </div>
            <div v-else-if="!videoUrl" class="empty-placeholder">
              <el-icon class="placeholder-icon"><VideoPlay /></el-icon>
              <div class="placeholder-text">在左侧输入你的想法，开始创作吧</div>
            </div>
            <div v-else class="video-container">
              <video 
                :src="videoUrl" 
                controls 
                class="video-player"
              ></video>
            </div>
          </el-card>
        </div>
      </el-container>
    </el-container>
    
    <!-- 用户登录/注册对话框 -->
    <user-dialog
      v-model:visible="userDialogVisible"
      @auth-success="handleAuthSuccess"
    />

    <!-- 历史视频对话框 -->
    <el-dialog
      v-model="historyDialogVisible"
      title="历史生成视频"
      width="80%"
      class="history-dialog"
    >
      <div v-if="historyVideos.length === 0" class="empty-history">
        <el-empty description="暂无历史记录" />
      </div>
      <div v-else>
        <el-table
          :data="historyVideos"
          style="width: 100%"
          border
          stripe
          :default-sort="{ prop: 'created_at', order: 'descending' }"
        >
          <el-table-column
            prop="created_at"
            label="生成时间"
            sortable
            width="180"
            :formatter="(row) => formatDate(row.created_at)"
          />
          <el-table-column
            prop="model"
            label="使用模型"
            width="150"
            :formatter="formatModelName"
          />
          <el-table-column
            prop="type"
            label="生成类型"
            width="120"
            :formatter="formatVideoType"
          />
          <el-table-column
            prop="prompt"
            label="提示词"
            show-overflow-tooltip
          />
          <el-table-column
            label="预览"
            width="180"
          >
            <template #default="scope">
              <div class="video-preview">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="previewVideo(scope.row)"
                >
                  播放预览
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            width="120"
          >
            <template #default="scope">
              <el-button 
                type="success" 
                size="small" 
                @click="downloadVideo(scope.row)"
              >
                下载
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[5, 10, 20]"
            layout="total, sizes, prev, pager, next"
            :total="totalVideos"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-dialog>

    <!-- 视频预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="视频预览"
      width="60%"
      class="preview-dialog"
    >
      <div v-if="previewVideoUrl" class="preview-container">
        <video 
          :src="previewVideoUrl" 
          controls 
          class="preview-player"
          autoplay
        ></video>
        <div class="video-details">
          <p><strong>提示词:</strong> {{ previewVideoData.prompt }}</p>
          <p><strong>模型:</strong> {{ formatModelName(previewVideoData) }}</p>
          <p><strong>生成时间:</strong> {{ formatDate(previewVideoData.created_at) }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ArrowRight, User, VideoPlay, Plus, RefreshRight, QuestionFilled, Histogram } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import UserDialog from '../components/auth/UserDialog.vue'
import UserProfile from '../components/auth/UserProfile.vue'
import axios from 'axios'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default {
  name: 'VideoView',
  components: {
    UserDialog,
    UserProfile,
    ArrowRight,
    User,
    VideoPlay,
    Plus,
    RefreshRight,
    QuestionFilled,
    Histogram
  },
  setup() {
    // 用户认证相关
    const isLoggedIn = ref(false)
    const currentUser = ref({})
    const userDialogVisible = ref(false)
    
    // 功能选择相关
    const activeFeature = ref('text-to-video')
    const showTextModelSelect = ref(false)
    const showImageModelSelect = ref(false)
    const selectedTextModel = ref('wanx2.1-t2v-turbo') // 默认选择turbo版
    const selectedImageModel = ref('wanx2.1-i2v-turbo') // 默认选择turbo版
    
    // 输入相关
    const promptText = ref('')
    const imageUrl = ref('')
    const imagePromptText = ref('')
    
    // 设置相关
    const selectedResolution = ref('720P') // 文生视频分辨率
    const selectedRatio = ref('16:9') // 文生视频比例
    const imageResolution = ref('720P') // 图生视频分辨率
    const videoDuration = ref(5) // 图生视频时长（秒）
    const seedValue = ref('') // 随机种子
    const promptExtend = ref(true) // 智能改写
    
    // 状态相关
    const loading = ref(false)
    const loadingProgress = ref(0)
    const loadingStatus = ref('')  // success / exception
    const loadingText = ref('正在生成视频...')
    const videoUrl = ref('')
    const taskId = ref('')
    const videoId = ref(null)
    const checkInterval = ref(null)
    const showCheckStatusButton = ref(false)
    
    // 历史视频相关
    const historyDialogVisible = ref(false)
    const historyVideos = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalVideos = ref(0)
    
    // 视频预览相关
    const previewDialogVisible = ref(false)
    const previewVideoUrl = ref('')
    const previewVideoData = ref({})
    
    // 监听文生视频模型变化，如果选择了plus模型，则自动切换到720P
    watch(selectedTextModel, (newModel) => {
      if (newModel === 'wanx2.1-t2v-plus' && selectedResolution.value === '480P') {
        selectedResolution.value = '720P'
      }
    })
    
    // 监听图生视频模型变化，如果选择了plus模型，则自动切换到720P
    watch(selectedImageModel, (newModel) => {
      if (newModel === 'wanx2.1-i2v-plus') {
        imageResolution.value = '720P'
        videoDuration.value = 5 // plus模型固定为5秒
      }
    })
    
    // 生成随机种子
    const generateRandomSeed = () => {
      seedValue.value = Math.floor(Math.random() * 2147483647)
    }
    
    // 获取分辨率具体值
    const getTextVideoResolution = computed(() => {
      const resolutionMap = {
        '720P': {
          '16:9': '1280*720',
          '9:16': '720*1280',
          '1:1': '960*960',
          '3:4': '832*1088',
          '4:3': '1088*832'
        },
        '480P': {
          '16:9': '832*480',
          '9:16': '480*832',
          '1:1': '624*624'
        }
      }
      
      return resolutionMap[selectedResolution.value][selectedRatio.value]
    })
    
    // 检查表单是否有效
    const isFormValid = computed(() => {
      if (activeFeature.value === 'text-to-video') {
        return promptText.value.trim().length > 0
      } else {
        return imageUrl.value && imagePromptText.value.trim().length > 0
      }
    })
    
    // 初始化检查用户登录状态
    const initUserState = () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        // 只有当 token 存在时才认为已登录
        isLoggedIn.value = true
        const userInfo = localStorage.getItem('user_info')
        if (userInfo) {
          try {
            currentUser.value = JSON.parse(userInfo)
          } catch (e) {
            console.error('解析用户信息失败', e)
            // 即使用户信息解析失败，只要有token，也认为是登录状态，但可能需要重新获取用户信息
            currentUser.value = {}
          }
        } else {
          // 如果只有token没有用户信息，可能需要调用API获取
          currentUser.value = {}
          // fetchUserProfile(); // 可以在这里添加获取用户信息的逻辑
        }
      } else {
        // Token 不存在，则未登录
        isLoggedIn.value = false
        currentUser.value = {}
      }
    }
    
    // 处理用户登录成功
    const handleAuthSuccess = (user) => {
      currentUser.value = user
      isLoggedIn.value = true
    }
    
    // 处理用户登出
    const handleLogout = () => {
      isLoggedIn.value = false
      currentUser.value = {}
    }
    
    // 显示用户对话框
    const showUserDialog = () => {
      userDialogVisible.value = true
    }
    
    // 处理功能选择
    const handleFeatureSelect = (feature) => {
      activeFeature.value = feature
      // 切换功能时关闭对应的模型选择
      if (feature === 'image-to-video') {
        showTextModelSelect.value = false
      } else {
        showImageModelSelect.value = false
      }
    }
    
    // 修改生成视频方法
    const generateVideo = async () => {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录以生成视频')
        showUserDialog()
        return
      }
      
      loading.value = true
      loadingProgress.value = 0
      loadingStatus.value = ''
      loadingText.value = '正在提交视频生成任务...'
      showCheckStatusButton.value = false
      videoUrl.value = '' // 重置视频URL
      taskId.value = ''   // 重置任务ID
      videoId.value = null // 重置视频ID
      
      try {
        let response
        
        if (activeFeature.value === 'text-to-video') {
          // 对于文生视频，使用普通JSON格式
          const payload = {
            model: selectedTextModel.value,
            prompt: promptText.value,
            prompt_extend: promptExtend.value,
            size: getTextVideoResolution.value
          }
          if (seedValue.value) {
            payload.seed = parseInt(seedValue.value) // 确保种子是数字
          }
          
          response = await axios.post('/api/video/text-to-video', payload)
        } else {
          // 对于图生视频，使用FormData格式
          const params = new FormData()
          params.append('model', selectedImageModel.value)
          params.append('prompt', imagePromptText.value)
          params.append('prompt_extend', promptExtend.value)
          params.append('resolution', imageResolution.value)
          
          if (selectedImageModel.value === 'wanx2.1-i2v-turbo') {
            params.append('duration', videoDuration.value)
          }
          
          if (seedValue.value) {
            params.append('seed', seedValue.value)
          }
          
          // 处理图片
          if (imageFile.value) {
            params.append('image', imageFile.value)
          }
          
          response = await axios.post('/api/video/image-to-video', params)
        }
        
        // 处理响应
        if (response.data.success) {
          taskId.value = response.data.data.task_id
          videoId.value = response.data.data.video_id
          loadingText.value = '任务已提交，系统开始生成视频...'
          loadingProgress.value = 10
          ElMessage.success('视频生成任务已提交')
          startPollingTaskStatus()
        } else {
          throw new Error(response.data.message || '提交任务失败')
        }
        
      } catch (error) {
        console.error('生成视频失败:', error)
        loadingText.value = `生成失败: ${error.message || '未知错误'}`
        loadingStatus.value = 'exception'
        loadingProgress.value = 100
        showCheckStatusButton.value = true
        ElMessage.error('生成视频失败: ' + (error.response?.data?.message || error.message))
        // 确保即使失败也停止加载状态
        // loading.value = false;
        // 取消上面这行，失败时保持加载状态以便显示错误
      }
    }
    
    // 开始轮询任务状态
    const startPollingTaskStatus = () => {
      // 清除可能存在的旧定时器
      if (checkInterval.value) {
        clearInterval(checkInterval.value)
      }
      
      // 设置进度为等待状态
      loadingProgress.value = 20
      
      // 创建新的轮询间隔 (每10秒检查一次状态)
      checkInterval.value = setInterval(async () => {
        try {
          await checkTaskStatus()
        } catch (error) {
          console.error('检查任务状态失败:', error)
          loadingText.value = `检查状态失败: ${error.message || '未知错误'}`
          
          // 如果连续失败超过一定次数，停止轮询并显示手动检查按钮
          showCheckStatusButton.value = true
          clearInterval(checkInterval.value)
        }
      }, 10000) // 10秒检查一次
      
      // 立即执行一次检查
      checkTaskStatus()
    }
    
    // 添加图片文件引用
    const imageFile = ref(null)
    
    // 检查任务状态
    const checkTaskStatus = async () => {
      if (!taskId.value) return
      
      try {
        loadingText.value = '正在检查任务状态...'
        const response = await axios.get(`/api/video/task/${taskId.value}`)
        
        if (response.data.success) {
          const taskData = response.data.data
          const status = taskData.status
          
          // 根据状态更新UI
          switch (status) {
            case 'PENDING':
              loadingText.value = '任务待处理中...'
              loadingProgress.value = 20
              break
              
            case 'RUNNING':
              loadingText.value = '视频正在生成中，请耐心等待...'
              loadingProgress.value = 50
              break
              
            case 'SUCCEEDED':
              loadingText.value = '视频生成成功！'
              loadingStatus.value = 'success'
              loadingProgress.value = 100
              
              // 设置视频URL
              if (taskData.video_url) {
                videoUrl.value = taskData.video_url
              } else if (taskData.local_path) {
                videoUrl.value = `/api/video/play/${taskData.local_path.split('/').pop()}`
              }
              
              // 停止轮询
              clearInterval(checkInterval.value)
              
              // 延迟隐藏加载状态，让用户看到成功提示
              setTimeout(() => {
                loading.value = false
              }, 1500)
              
              ElMessage.success('视频生成成功!')
              break
              
            case 'FAILED':
              loadingText.value = `生成失败: ${taskData.error_message || '未知错误'}`
              loadingStatus.value = 'exception'
              loadingProgress.value = 100
              
              // 停止轮询
              clearInterval(checkInterval.value)
              
              ElMessage.error('视频生成失败: ' + (taskData.error_message || '未知错误'))
              break
              
            default:
              loadingText.value = `未知状态: ${status}`
              break
          }
        } else {
          throw new Error(response.data.message || '获取任务状态失败')
        }
      } catch (error) {
        console.error('检查任务状态失败:', error)
        // 不直接设置异常状态，因为这可能只是临时网络问题
        loadingText.value = '检查状态失败，稍后重试...'
        showCheckStatusButton.value = true
        throw error
      }
    }
    
    // 清理轮询间隔
    onUnmounted(() => {
      if (checkInterval.value) {
        clearInterval(checkInterval.value)
      }
    })
    
    // 修改上传图片处理方法，避免重复使用image_url
    const handleImageChange = (file) => {
      const isImage = file.raw.type.indexOf('image/') !== -1
      if (!isImage) {
        ElMessage.error('只能上传图片文件!')
        return
      }
      
      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isLt10M) {
        ElMessage.error('图片大小不能超过10MB!')
        return
      }
      
      // 保存文件引用
      imageFile.value = file.raw
      
      // 创建预览URL
      imageUrl.value = URL.createObjectURL(file.raw)
    }
    
    // 选择文生视频模型后自动关闭选择界面
    const handleTextModelChange = () => {
      setTimeout(() => {
        showTextModelSelect.value = false
      }, 300) // 延迟300毫秒关闭，让用户看到选择效果
    }
    
    // 选择图生视频模型后自动关闭选择界面
    const handleImageModelChange = () => {
      setTimeout(() => {
        showImageModelSelect.value = false
      }, 300) // 延迟300毫秒关闭，让用户看到选择效果
    }
    
    // 打开历史对话框
    const openHistoryDialog = () => {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录以查看历史记录')
        showUserDialog()
        return
      }
      
      historyDialogVisible.value = true
      fetchHistoryVideos()
    }
    
    // 获取历史视频列表
    const fetchHistoryVideos = async () => {
      // 再次确认用户已登录状态 (基于 token 的 initUserState 应该已经保证了)
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录以查看历史记录')
        // showUserDialog(); // initUserState 应该已经处理了
        return
      }
      
      const token = localStorage.getItem('auth_token')
      // 理论上此时 token 必然存在，因为 isLoggedIn 是基于它设置的
      // 但为保险起见，再次检查
      if (!token) {
        console.error('fetchHistoryVideos: isLoggedIn is true but token is missing!')
        ElMessage.error('认证信息丢失，请重新登录')
        handleLogout() 
        showUserDialog()
        return
      }
      
      try {
        console.log('Fetching history with token:', token ? '******' : 'null'); // 调试日志，不显示完整token
        const response = await axios.get('/api/video/my-videos', {
          params: {
            page: currentPage.value,
            per_page: pageSize.value
          },
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (response.data.success) {
          historyVideos.value = response.data.data.videos
          totalVideos.value = response.data.data.total
        } else {
          ElMessage.error(response.data.message || '获取历史记录失败')
        }
      } catch (error) {
        console.error('获取历史视频失败:', error)
        if (error.response && error.response.status === 401) {
          ElMessage.error('认证过期或无效，请重新登录')
          handleLogout()
          showUserDialog()
        } else {
          // 其他错误 (包括 405)
          ElMessage.error('获取历史视频失败: ' + (error.response?.data?.message || error.message) + ` (Status: ${error.response?.status})`)
        }
      }
    }
    
    // 处理分页大小变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      fetchHistoryVideos()
    }
    
    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchHistoryVideos()
    }
    
    // 预览视频
    const previewVideo = (video) => {
      previewVideoData.value = video
      previewVideoUrl.value = video.video_url || `/api/video/play/${video.local_path.split('/').pop()}`
      previewDialogVisible.value = true
    }
    
    // 下载视频
    const downloadVideo = async (video) => {
      try {
        // 获取视频URL
        const videoUrl = video.video_url || `/api/video/play/${video.local_path.split('/').pop()}`
        
        // 创建临时链接并点击下载
        const link = document.createElement('a')
        link.href = videoUrl
        link.download = `video_${video.id}_${new Date().getTime()}.mp4`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        ElMessage.success('开始下载视频')
      } catch (error) {
        console.error('下载视频失败:', error)
        ElMessage.error('下载视频失败: ' + error.message)
      }
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      
      try {
        const date = new Date(dateString)
        return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
      } catch (e) {
        return dateString
      }
    }
    
    // 格式化模型名称
    const formatModelName = (row) => {
      const modelMap = {
        'wanx2.1-t2v-turbo': '文生视频 2.1 极速',
        'wanx2.1-t2v-plus': '文生视频 2.1 专业',
        'wanx2.1-i2v-turbo': '图生视频 2.1 极速',
        'wanx2.1-i2v-plus': '图生视频 2.1 专业'
      }
      
      return modelMap[row.model] || row.model
    }
    
    // 格式化视频类型
    const formatVideoType = (row) => {
      const typeMap = {
        'text-to-video': '文生视频',
        'image-to-video': '图生视频'
      }
      
      return typeMap[row.type] || row.type
    }
    
    // 初始化
    onMounted(() => {
      initUserState()
    })
    
    return {
      // 用户相关
      isLoggedIn,
      currentUser,
      userDialogVisible,
      showUserDialog,
      handleAuthSuccess,
      handleLogout,
      
      // 功能选择相关
      activeFeature,
      showTextModelSelect,
      showImageModelSelect,
      selectedTextModel,
      selectedImageModel,
      handleFeatureSelect,
      handleTextModelChange,
      handleImageModelChange,
      
      // 输入相关
      promptText,
      imageUrl,
      imagePromptText,
      handleImageChange,
      
      // 设置相关
      selectedResolution,
      selectedRatio,
      imageResolution,
      videoDuration,
      seedValue,
      promptExtend,
      generateRandomSeed,
      getTextVideoResolution,
      
      // 状态相关
      loading,
      loadingProgress,
      loadingStatus,
      loadingText,
      videoUrl,
      taskId,
      videoId,
      checkTaskStatus,
      showCheckStatusButton,
      isFormValid,
      
      // 操作
      generateVideo,
      
      // 历史视频相关
      historyDialogVisible,
      historyVideos,
      currentPage,
      pageSize,
      totalVideos,
      openHistoryDialog,
      handleSizeChange,
      handleCurrentChange,
      
      // 预览相关
      previewDialogVisible,
      previewVideoUrl,
      previewVideoData,
      previewVideo,
      
      // 工具方法
      formatDate,
      formatModelName,
      formatVideoType,
      downloadVideo
    }
  }
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-img {
  height: 40px;
  margin-right: 10px;
}

.logo h1 {
  font-size: 1.5rem;
  margin: 0;
}

.el-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.login-button {
  border-radius: 20px;
}

.rounded-button {
  border-radius: 20px;
  padding: 8px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.rounded-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

.main-container {
  flex: 1;
  overflow: hidden;
  padding: 20px;
  background-color: var(--el-fill-color-lighter);
  display: flex;
}

.control-panel {
  width: 320px;
  padding-right: 15px;
}

.control-panel-card {
  height: 100%;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.control-panel-inner {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-title {
  font-size: 1.3rem;
  margin-bottom: 20px;
  color: var(--el-text-color-primary);
}

.feature-buttons {
  margin-bottom: 20px;
}

.button-row {
  display: flex;
  gap: 15px;
}

.button-group {
  flex: 1;
  position: relative;
}

.feature-btn {
  border-radius: 20px;
  height: 40px;
  width: 100%;
  position: relative;
  display: flex;
  align-items: center;
  padding: 0 35px 0 15px;
}

.feature-btn-text {
  text-align: center;
  flex: 1;
  padding-right: 5px; /* 为右边的按钮留出更多空间 */
}

.active-btn {
  background-color: var(--el-color-primary);
  color: white;
}

.model-select-btn {
  position: absolute;
  right: 2px;
  top: 4px;
  height: 32px;
  width: 32px; /* 缩小按钮宽度 */
  border-radius: 0 20px 20px 0;
  padding: 0;
  margin: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: transparent; /* 使按钮背景透明 */
  border: none;
  color: inherit; /* 继承父按钮的文字颜色 */
}

.model-select-card {
  margin: 15px 0;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.model-options h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1rem;
}

.model-radio-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

.model-radio {
  margin-right: 0;
  padding: 40px 12px;
  border-radius: 10px;
  border: 1px solid var(--el-border-color-light);
  width: 100%;
}

.model-radio:hover {
  background-color: var(--el-fill-color-light);
}

.model-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
  flex-wrap: wrap;
}

.model-name {
  font-weight: bold;
  white-space: nowrap;
  font-size: 0.95rem;
}

.model-desc-tooltip {
  margin-left: 2px;
}

.input-section {
  margin-top: 20px;
}

.input-title {
  font-size: 1rem;
  margin-bottom: 10px;
  color: var(--el-text-color-primary);
}

.prompt-input {
  border-radius: 20px;
  margin-bottom: 5px;
}

.input-counter {
  text-align: right;
  font-size: 0.8rem;
  color: var(--el-text-color-secondary);
  margin-bottom: 15px;
}

.image-uploader {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.upload-placeholder {
  width: 100%;
  height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border: 1px dashed var(--el-border-color);
  border-radius: 12px;
  cursor: pointer;
}

.upload-placeholder:hover {
  border-color: var(--el-color-primary);
}

.upload-text {
  margin-top: 10px;
  font-size: 0.9rem;
  color: var(--el-text-color-secondary);
}

.upload-hint {
  margin-top: 5px;
  font-size: 0.8rem;
  color: var(--el-text-color-secondary);
}

.uploaded-image {
  max-width: 100%;
  max-height: 150px;
  object-fit: contain;
  border-radius: 12px;
}

.resolution-section {
  margin-top: 20px;
}

.resolution-selector {
  margin-bottom: 15px;
}

.resolution-radios {
  display: flex;
  gap: 15px;
}

.resolution-radios :deep(.el-radio) {
  margin-right: 0;
  border-radius: 20px;
  overflow: hidden;
}

.resolution-radios :deep(.el-radio__label) {
  padding: 0 15px;
}

.ratio-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.ratio-btn {
  flex: 1;
  min-width: 60px;
  border-radius: 20px;
  height: 35px;
}

.ratio-btn-active {
  background-color: var(--el-color-primary);
  color: white;
  border-color: var(--el-color-primary);
}

.duration-section {
  margin-top: 20px;
}

.duration-slider {
  padding: 0 10px;
  margin-bottom: 20px;
}

.seed-section {
  margin-top: 20px;
}

.seed-input {
  border-radius: 20px;
  margin-bottom: 5px;
}

.seed-hint {
  font-size: 0.8rem;
  color: var(--el-text-color-secondary);
  margin-bottom: 15px;
}

.option-switches {
  margin-top: 20px;
  margin-bottom: 25px;
}

.switch-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.switch-label {
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-icon {
  font-size: 14px;
  color: var(--el-color-info);
  cursor: pointer;
}

.info-icon:hover {
  color: var(--el-color-primary);
}

.generate-button-container {
  margin-top: auto;
}

.generate-button {
  width: 100%;
  height: 45px;
  border-radius: 22.5px;
  font-size: 1.1rem;
  position: relative;
}

.credits {
  position: absolute;
  right: 15px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 2px 8px;
  font-size: 0.8rem;
}

.video-display {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-left: 15px;
}

.video-display-card {
  width: 100%;
  height: 100%;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 30px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 90%;
}

.loading-text {
  margin-top: 20px;
  font-size: 1.2rem;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.loading-tip {
  margin-top: 10px;
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
}

.loading-actions {
  margin-top: 15px;
}

.empty-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--el-text-color-secondary);
  height: 100%;
  width: 100%;
}

.placeholder-icon {
  font-size: 5rem;
  margin-bottom: 20px;
}

.placeholder-text {
  font-size: 1.2rem;
}

.video-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.video-player {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.video-actions {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 10;
}

.history-button {
  border-radius: 20px;
  padding: 8px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.history-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

.history-dialog {
  --el-dialog-padding-primary: 20px;
}

.empty-history {
  padding: 30px 0;
  text-align: center;
}

.video-preview {
  display: flex;
  justify-content: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.preview-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.preview-player {
  max-width: 100%;
  max-height: 60vh;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.video-details {
  width: 100%;
  padding: 15px;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;
}

.video-details p {
  margin: 8px 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .control-panel {
    width: 100%;
    padding-right: 0;
    margin-bottom: 15px;
  }
  
  .main-container {
    flex-direction: column;
  }
  
  .button-row {
    flex-direction: column;
  }
  
  .video-display {
    padding-left: 0;
  }
}
</style> 