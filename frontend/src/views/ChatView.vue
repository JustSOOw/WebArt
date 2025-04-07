<template>
  <div class="app-container chat-page">
    <el-container>
      <!-- 顶部标题栏 -->
      <el-header height="70px">
        <div class="logo">
          <img src="../assets/logo.svg" alt="WordArt锦书" class="logo-img" />
          <h1>WordArt锦书 - AI对话</h1>
        </div>
        <div class="header-actions">
          <user-profile 
            v-if="isLoggedIn" 
            :user="currentUser" 
            :show-image-history-option="false" 
            @logout="handleLogout"
          />
          <el-button v-else link type="primary" @click="showUserDialog">
            <el-icon><User /></el-icon>
            登录/注册
          </el-button>
        </div>
      </el-header>
      
      <el-container class="main-container">
        <!-- 左侧对话历史列表 -->
        <el-aside width="20%" class="conversation-panel">
          <chat-history 
            :conversations="conversations"
            :activeConversationId="selectedConversationId"
            @select-conversation="handleSelectConversation"
            @new-conversation="handleNewConversation"
            @delete-conversation="deleteConversation"
            @rename-conversation="renameConversation"
          />
        </el-aside>
        
        <!-- 右侧主内容区 -->
        <el-main class="chat-display">
          <!-- 模型选择器 -->
          <model-selector
            :model="currentModel"
            :available-models="availableModels"
            @model-change="handleModelChange"
          />

          <!-- 消息列表直接放置在主容器中 -->
          <message-list 
            ref="messageListRef"
            class="messages-area"
            :messages="conversationMessages"
            :loading="isConversationLoading"
          />
          
          <!-- 输入区域设置为固定悬浮 -->
          <div class="input-container">
            <chat-input 
              :loading="isProcessing"
              :supported-file-types="supportedFileTypes"
              :show-upload="currentModelCapabilities.includes('image')"
              :model-id="currentModel"
              @send-message="sendMessage"
              @upload-file="handleFileUpload"
              @upload-files="handleMultiFileUpload"
              @send-multi-images="handleSendMultiImages"
            />
          </div>
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 用户登录/注册对话框 -->
    <user-dialog
      v-model:visible="userDialogVisible"
      :initial-mode="userDialogMode"
      @auth-success="handleAuthSuccess"
    />
  </div>
</template>

<script>
import { ref, computed, reactive, onMounted, watch, nextTick } from 'vue'
import { User, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { v4 as uuidv4 } from 'uuid'
import UserProfile from '../components/auth/UserProfile.vue'
import UserDialog from '../components/auth/UserDialog.vue'
import ChatHistory from '../components/chat/ChatHistory.vue'
import MessageList from '../components/chat/MessageList.vue'
import ModelSelector from '../components/chat/ModelSelector.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import { isAuthenticated, getCurrentUser, logout, authFetch } from '../utils/auth'

// 添加超时处理函数
const fetchWithTimeout = async (url, options, timeout = 30000) => {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  // 对于Omni模型路径，延长日志记录
  if (url.includes('omni-completions')) {
    console.log('正在请求Omni模型，超时设置为:', timeout, 'ms');
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    if (error.name === 'AbortError') {
      console.error('请求超时:', url);
      throw new Error('请求超时，请稍后重试');
    }
    console.error('请求出错:', error);
    throw error;
  }
};

export default {
  name: 'ChatView',
  components: {
    UserProfile,
    UserDialog,
    ChatHistory,
    MessageList,
    ModelSelector,
    ChatInput,
    User,
    ChatDotRound
  },
  setup() {
    // 用户相关状态
    const isLoggedIn = ref(false)
    const currentUser = ref(null)
    const userDialogVisible = ref(false)
    const userDialogMode = ref('login')
    
    // 对话相关状态
    const conversations = ref([])
    const selectedConversationId = ref(null)
    const conversationMessages = ref([])
    const isConversationLoading = ref(false)
    const isProcessing = ref(false)
    
    // 模型相关状态
    const availableModels = ref([
      { id: 'qwen-turbo', name: '通义千问-Turbo', capabilities: ['text'] },
      { id: 'qwen-plus', name: '通义千问-Plus', capabilities: ['text'] },
      { id: 'qwen-max-latest', name: '通义千问-Max', capabilities: ['text'] },
      { id: 'qwen-omni-turbo', name: '通义千问-Omni', capabilities: ['text', 'image', 'audio', 'video'] }
    ])
    const currentModel = ref('qwen-max-latest')
    
    // 文件上传设置
    const supportedFileTypes = computed(() => {
      const model = availableModels.value.find(m => m.id === currentModel.value)
      if (!model) return []
      
      const types = []
      // 文档文件类型
      if (model.capabilities.includes('file') || model.capabilities.includes('text')) {
        types.push('.pdf', '.docx', '.txt')
      }
      // 图片文件类型
      if (model.capabilities.includes('image')) {
        types.push('.png', '.jpg', '.jpeg', '.gif')
      }
      // 音频文件类型
      if (model.capabilities.includes('audio')) {
        types.push('.mp3', '.wav', '.m4a')
      }
      // 视频文件类型
      if (model.capabilities.includes('video')) {
        types.push('.mp4', '.mov', '.avi')
      }
      
      console.log('当前模型支持的文件类型:', types)
      return types
    })
    

    
    // 添加消息列表引用
    const messageListRef = ref(null)

    // 用户认证相关方法
    const showUserDialog = () => {
      userDialogVisible.value = true
      userDialogMode.value = 'login'
    }
    
    const handleAuthSuccess = (user) => {
      isLoggedIn.value = true
      currentUser.value = user
      userDialogVisible.value = false
      
      // 加载用户的对话列表
      fetchUserConversations()
    }
    
    const handleLogout = async () => {
      try {
        await authFetch('/api/auth/logout', {
          method: 'POST'
        })
      } catch (error) {
        console.error('登出请求失败:', error)
      }
      
      // 无论后端请求是否成功，都清除本地状态
      logout()
      isLoggedIn.value = false
      currentUser.value = null
      
      // 清空对话数据
      conversations.value = []
      conversationMessages.value = []
      selectedConversationId.value = null
    }
    
    // 对话相关方法
    const fetchUserConversations = async () => {
      isConversationLoading.value = true;
      try {
        // 始终从本地数据库加载对话
        console.log('从本地数据库加载对话');
        conversations.value = await loadConversationsFromDB();
      } catch (error) {
        console.error('获取对话出错:', error);
        conversations.value = [];
      } finally {
        isConversationLoading.value = false;
      }
    };
    

    
    // 选择对话
    const handleSelectConversation = async (conversationId) => {
      console.log('选择对话:', conversationId);
      // 类型检查，确保conversationId是有效值
      if (!conversationId) {
        console.error('选择对话失败: conversationId为空');
        return;
      }
      
      try {
        // 设置选中状态
        selectedConversationId.value = conversationId;
        isConversationLoading.value = true;
        
        // 只从本地数据库加载消息
        console.log('从本地数据库加载消息');
        conversationMessages.value = await loadMessagesFromDB(conversationId);
        
        // 查找当前对话
        const selectedConversation = conversations.value.find(c => c.id === conversationId);
        if (selectedConversation) {
          currentModel.value = selectedConversation.model || 'qwen-max-latest';
        }
      } catch (error) {
        console.error('加载对话消息失败:', error);
        conversationMessages.value = [];
      } finally {
        isConversationLoading.value = false;
      }
    };
    

    
    // 创建新对话
    const handleNewConversation = async () => {
      try {
        isConversationLoading.value = true;
        let newConversation;
        
        if (isAuthenticated()) {
          // 尝试创建服务器对话
          const response = await authFetch('/api/chat/conversations', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              title: '新对话',
              model: currentModel.value,
            }),
          });

          if (response.ok) {
            const data = await response.json();
            newConversation = data.conversation;
            console.log('创建服务器对话成功:', newConversation);
          } else {
            console.warn('创建服务器对话失败，创建本地对话');
            // 失败时创建本地对话
            newConversation = createLocalConversation();
          }
        } else {
          // 未登录时创建本地对话
          newConversation = createLocalConversation();
        }

        // 添加到对话列表
        conversations.value.unshift(newConversation);
        
        // 保存到本地数据库
        await saveConversationToDB({
          ...newConversation,
          updatedAt: newConversation.updated_at || new Date().toISOString()
        });
        
        // 选择新对话
        selectedConversationId.value = newConversation.id;
        console.log('新对话ID已设置:', selectedConversationId.value);
        
        // 初始化空的对话消息数组
        conversationMessages.value = [];
        
        return newConversation.id; // 返回新创建的对话ID
      } catch (error) {
        console.error('创建对话失败:', error);
        ElMessage.error('创建对话失败');
        return null;
      } finally {
        isConversationLoading.value = false;
      }
    };
    
    // 创建本地对话
    const createLocalConversation = () => {
      const now = new Date().toISOString();
      const localId = `local-${Date.now()}`;
      console.log('创建本地对话，ID:', localId);
      return {
        id: localId,
        title: '新对话',
        model: currentModel.value,
        created_at: now,
        updated_at: now,
        updatedAt: now,
      };
    };
    
    // 消息相关方法
    const sendMessage = async (messageContent) => {
      if (!messageContent.trim()) return;
      
      isConversationLoading.value = true;
      
      try {
        const messageId = 'msg_' + Date.now();
        const timestamp = new Date().toISOString();
        
        // 确认选中对话ID，如果没有，创建新对话
        if (!selectedConversationId.value) {
          await handleNewConversation();
          // 确保handleNewConversation成功后再继续
          if (!selectedConversationId.value) {
            throw new Error("无法创建新对话");
          }
        }
        
        // 添加用户消息到界面
        const userMessage = {
          id: messageId,
          role: 'user',
          content: messageContent,
          created_at: timestamp,
          createdAt: timestamp,
          conversationId: selectedConversationId.value
        };
        
        conversationMessages.value.push(userMessage);
        
        // 保存到本地数据库
        await saveMessageToDB(userMessage);
        
        // 添加临时AI响应消息
        const tempAiMessage = {
          id: 'temp_' + Date.now(),
          role: 'assistant',
          content: '',
          created_at: timestamp,
          createdAt: timestamp,
          conversationId: selectedConversationId.value,
          isLoading: true
        };
        
        conversationMessages.value.push(tempAiMessage);
        
        // 更新对话标题（如果是新对话）
        if (conversations.value.find(c => c.id === selectedConversationId.value)?.title === '新对话') {
          renameConversation({ id: selectedConversationId.value, title: messageContent });
        }
        
        // 始终使用通用completions API，无论对话ID是什么
        const url = '/api/chat/completions';
        
        // 提取最近的几条消息
        const recentMessages = conversationMessages.value
          .filter(msg => !msg.isLoading && msg.role !== 'system')
          .slice(-5); // 最近5条消息
        
        // 根据模型格式化请求体
        let requestBody = {};
        
        if (currentModel.value === 'qwen-omni-turbo') {
          // OMNI模型的特殊格式 - 根据官方文档实现纯文本输入
          requestBody = {
            model: currentModel.value,
            messages: recentMessages.map(msg => ({
              role: msg.role,
              content: msg.content // 纯文本内容
            })),
            // 必须添加modalities字段，指定仅输出文本
            modalities: ["text"],
            // stream 必须设置为 True
            stream: true,
            stream_options: {"include_usage": true}
          };
          
          // 添加系统消息
          if (!requestBody.messages.some(msg => msg.role === 'system')) {
            requestBody.messages.unshift({
              role: 'system',
              content: '你是WordArt锦书AI助手，由通义千问大语言模型驱动。'
            });
          }
          
          // 添加日志输出以便调试
          console.log('使用Omni模型，特殊格式请求体:', JSON.stringify(requestBody));
        } else {
          // 标准模型格式
          requestBody = {
            model: currentModel.value,
            messages: recentMessages.map(msg => ({
              role: msg.role,
              content: msg.content
            })),
            stream: true
          };
        }
        
        console.log('发送请求到:', url, '请求体:', requestBody);
        
        // 发送API请求
        const response = await fetchWithTimeout(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(isLoggedIn.value ? {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            } : {})
          },
          body: JSON.stringify(requestBody),
        }, currentModel.value === 'qwen-omni-turbo' ? 120000 : 60000); // Omni模型使用120秒超时
        
        if (!response.ok) {
          console.error('API请求失败:', response.status, response.statusText);
          
          // 针对Omni模型的特殊错误处理
          if (currentModel.value === 'qwen-omni-turbo') {
            throw new Error(`Omni模型请求失败，可能是模型服务不可用或配置错误，请尝试其他模型。状态码: ${response.status}`);
          } else {
            throw new Error(`请求失败: ${response.status} ${response.statusText}`);
          }
        }
        
        // 处理流式响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let aiResponse = '';
        let aiMessageId = '';
        
        // 删除临时消息
        conversationMessages.value.pop();
        
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n').filter(line => line.trim() !== '');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.substring(6);
                if (data === '[DONE]') continue;
                
                try {
                  const parsed = JSON.parse(data);
                  
                  // 处理错误响应
                  if (parsed.error) {
                    throw new Error(parsed.message || 'AI生成回复失败');
                  }
                  
                  if (!aiMessageId && parsed.id) {
                    aiMessageId = parsed.id;
                  }
                  
                  // 处理Omni模型的特殊响应格式
                  if (currentModel.value === 'qwen-omni-turbo') {
                    if (parsed.choices && parsed.choices[0]) {
                      const delta = parsed.choices[0].delta;
                      if (delta && delta.content) {
                        aiResponse += delta.content;
                        
                        // 更新或添加AI消息
                        const existingMsgIndex = conversationMessages.value.findIndex(m => m.id === aiMessageId);
                        
                        if (existingMsgIndex >= 0) {
                          conversationMessages.value[existingMsgIndex].content = aiResponse;
                        } else {
                          conversationMessages.value.push({
                            id: aiMessageId,
                            role: 'assistant',
                            content: aiResponse,
                            created_at: new Date().toISOString(),
                            createdAt: new Date().toISOString(),
                            conversationId: selectedConversationId.value
                          });
                        }
                      }
                    }
                  } else {
                    // 处理标准模型的响应格式
                    if (parsed.choices && parsed.choices[0]) {
                      const delta = parsed.choices[0].delta;
                      if (delta && delta.content) {
                        aiResponse += delta.content;
                        
                        // 更新或添加AI消息
                        const existingMsgIndex = conversationMessages.value.findIndex(m => m.id === aiMessageId);
                        
                        if (existingMsgIndex >= 0) {
                          conversationMessages.value[existingMsgIndex].content = aiResponse;
                        } else {
                          conversationMessages.value.push({
                            id: aiMessageId,
                            role: 'assistant',
                            content: aiResponse,
                            created_at: new Date().toISOString(),
                            createdAt: new Date().toISOString(),
                            conversationId: selectedConversationId.value
                          });
                        }
                      }
                    }
                  }
                } catch (err) {
                  console.error('解析流数据错误:', err, data);
                  throw err;
                }
              }
            }
          }
        } catch (error) {
          console.error('读取流响应错误:', error);
          // 如果在接收流过程中发生错误，但已经有部分响应，不抛出错误
          if (!aiResponse) {
            throw error;
          }
        } finally {
          // 确保AI消息被添加并保存
          if (aiResponse) {
            const finalAiMessage = {
              id: aiMessageId || 'ai_' + Date.now(),
              role: 'assistant',
              content: aiResponse,
              created_at: new Date().toISOString(),
              createdAt: new Date().toISOString(),
              conversationId: selectedConversationId.value
            };
            
            // 检查是否已存在此消息
            const existingMsgIndex = conversationMessages.value.findIndex(m => m.id === finalAiMessage.id);
            if (existingMsgIndex >= 0) {
              conversationMessages.value[existingMsgIndex] = finalAiMessage;
            } else {
              conversationMessages.value.push(finalAiMessage);
            }
            
            // 保存到本地数据库
            await saveMessageToDB(finalAiMessage);
            
            // 更新对话最后修改时间
            const conversation = conversations.value.find(c => c.id === selectedConversationId.value);
            if (conversation) {
              conversation.updated_at = new Date().toISOString();
              conversation.updatedAt = new Date().toISOString();
              await saveConversationToDB(conversation);
            }
          }
        }
      } catch (error) {
        console.error('发送消息错误:', error);
        
        // 移除临时消息
        const tempIndex = conversationMessages.value.findIndex(m => m.isLoading);
        if (tempIndex >= 0) {
          conversationMessages.value.splice(tempIndex, 1);
        }
        
        // 添加错误消息
        conversationMessages.value.push({
          id: 'error_' + Date.now(),
          role: 'system',
          content: `发送失败: ${error.message}. 请重试或检查网络连接。`,
          created_at: new Date().toISOString(),
          createdAt: new Date().toISOString(),
          conversationId: selectedConversationId.value,
          error: true
        });
      } finally {
        isConversationLoading.value = false;
      }
    };
    
    // 更新对话标题 - 重命名为 renameConversation 并修改逻辑
    const renameConversation = async ({ id, title }) => { // 接受对象参数
      try {
        // 类型检查
        if (!id || !title) {
          console.error('重命名对话失败: ID 或标题为空', { id, title });
          return;
        }
        
        // 更新内存中的对话标题
        const conversation = conversations.value.find(c => c.id === id);
        if (conversation) {
          conversation.title = title; // 直接使用新标题
          conversation.updated_at = new Date().toISOString(); // 更新修改时间
          conversation.updatedAt = conversation.updated_at;  // 保持一致
          
          // 保存到本地数据库
          await saveConversationToDB({
            ...conversation,
            updatedAt: conversation.updated_at || new Date().toISOString()
          });
          
          console.log('对话标题已更新并保存到本地数据库:', title);
        }
      } catch (error) {
        console.error('更新对话标题失败:', error);
      }
    };
    
    // 处理文件上传
    const handleFileUpload = async ({ file, message: userMessage }) => { // 修改参数接收方式
      // 增加空值检查
      if (!file) {
        console.error('handleFileUpload 接收到的文件为空');
        ElMessage.error('文件上传失败：未找到文件数据');
        return;
      }
      
      try {
        isConversationLoading.value = true
        
        // 获取文件扩展名
        const fileExtension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase()
        
        // 保存用户输入的消息
        file.customMessage = userMessage;
        
        // 首先创建用户消息对象，但不立即添加到界面(因为sendMultiModalMessage会添加一个临时消息)
        let userMessageId = 'temp_' + Date.now();
        let userContent = userMessage || ' '; // 确保至少有一个空格作为内容
        
        // 创建临时用户消息对象(不立即添加到conversationMessages.value)
        const tempUserMessage = {
          id: userMessageId,
          role: 'user',
          content: userContent,
          created_at: new Date().toISOString(),
          createdAt: new Date().toISOString(),
          conversationId: selectedConversationId.value,
          file: {
            name: file.name,
            size: file.size,
            type: file.type
          }
        };
        
        // 移除添加临时消息的代码：
        // conversationMessages.value.push(tempUserMessage);

        // 检查文件类型和大小
        if (!supportedFileTypes.value.includes(fileExtension)) {
          ElMessage.error(`不支持的文件类型: ${fileExtension}`)
          isConversationLoading.value = false
          return
        }
        
        
        // 记录日志
        console.log('准备上传文件:', file.name, '大小:', file.size, '类型:', file.type)
        
        // 检查文件是否为File对象
        if (!(file instanceof File) && file.raw) {
          console.log('转换Element-UI原始文件对象为File对象')
          file = file.raw
        }
        
        // 对于Omni模型的媒体文件，直接使用Base64编码
        if (currentModel.value === 'qwen-omni-turbo' && 
            (isImageFile(fileExtension) || isAudioFile(fileExtension) || isVideoFile(fileExtension))) {
          
          // 针对音频文件的特殊处理 
          if (isAudioFile(fileExtension)) {
            // 额外的音频时长检查
            if (file.size > 7.5 * 1024 * 1024) { // 7.5MB
              ElMessage.error(`音频文件大小超过限制，最大支持7.5MB（Base64编码后约10MB），时长最长3分钟`);
              isConversationLoading.value = false;
              return;
            }
          }
          
          // 添加额外的基于API限制的大小检查
          const API_BASE64_LIMIT = 10 * 1024 * 1024; // 10MB Base64限制
          // Base64编码会使数据增大约33%
          const estimatedBase64Size = Math.ceil(file.size * 1.33);
          
          if (estimatedBase64Size > API_BASE64_LIMIT) {
            ElMessage.error(`文件大小转换为Base64后超过API限制: 约${(estimatedBase64Size / 1024 / 1024).toFixed(2)}MB > 10MB`);
            isConversationLoading.value = false;
            return;
          }
          
          // 读取文件为Base64
          const base64Data = await readFileAsBase64(file);
          console.log('文件已转换为Base64编码（显示前20个字符）:', base64Data.substring(0, 20) + '...');
          console.log('Base64编码后大小:', Math.ceil(base64Data.length / 1024), 'KB');
          
          // 获取媒体类型
          const mediaType = getMediaType(fileExtension);
          
          // 使用多模态API发送带有Base64文件的消息
          // 修正：直接使用函数参数 userMessage，而不是 file.customMessage
          await sendMultiModalMessageWithBase64(userMessage || '', mediaType, base64Data, fileExtension);
          
          isConversationLoading.value = false;
          return;
        }
        
        // 其他文件或非Omni模型继续使用原来的上传方式
        // 创建FormData - 不要设置任何Content-Type头
        const formData = new FormData()
        formData.append('file', file)
        
        // 记录请求信息
        console.log('FormData中的项目:', [...formData.entries()].map(e => e[0]))
        
        // 发送上传请求 - 不要设置Content-Type头
        console.log('发送上传请求...')
        const uploadResponse = await fetch('/api/chat/upload', {
          method: 'POST',
          headers: isLoggedIn.value ? {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          } : {},
          body: formData
        })
        
        // 记录上传状态
        console.log('上传响应状态:', uploadResponse.status, uploadResponse.statusText)
        
        if (!uploadResponse.ok) {
          const responseText = await uploadResponse.text()
          console.log('上传响应内容:', responseText)
          
          try {
            // 尝试解析为JSON
            const responseData = JSON.parse(responseText)
            console.error('文件上传失败:', responseData.message || '未知错误')
            ElMessage.error(responseData.message || '文件上传失败')
          } catch (e) {
            // 如果无法解析为JSON，直接显示文本
            console.error('文件上传失败:', responseText)
            ElMessage.error(`文件上传失败: ${responseText}`)
          }
          
          isConversationLoading.value = false
          return
        }
        
        // 解析上传结果
        const responseText = await uploadResponse.text()
        let uploadData
        try {
          uploadData = JSON.parse(responseText)
          
          // 获取媒体类型
          const mediaType = getMediaType(fileExtension)
          
          // 使用用户输入的内容，不使用默认提示
          let messageContent = file.customMessage || '';
          
          // 更新临时消息为永久消息
          const tempIndex = conversationMessages.value.findIndex(m => m.id === userMessageId)
          if (tempIndex >= 0) {
            const permanentUserMessage = {
              ...tempUserMessage,
              id: uuidv4(),
              media_type: mediaType,
              media_url: uploadData.url
            };
            conversationMessages.value[tempIndex] = permanentUserMessage;
            
            // 保存到数据库
            await saveMessageToDB(permanentUserMessage);
          }
          
          // 判断当前模型是否为多模态模型
          if (currentModel.value === 'qwen-omni-turbo') {
            // 使用多模态API发送消息
            await sendMultiModalMessage(messageContent, mediaType, uploadData.url)
          } else {
            // 文本模型只能发送链接
            if (mediaType === 'image') {
              // 图片可以用markdown格式
              await sendMessage(`${messageContent} ![${uploadData.filename}](${uploadData.url})`.trim())
            } else {
              // 其他文件用链接
              await sendMessage(`${messageContent} [${uploadData.filename}](${uploadData.url})`.trim())
            }
          }
          
          ElMessage.success('文件上传成功')
        } catch (e) {
          console.error('文件上传失败:', e)
          ElMessage.error('文件处理失败')
        } finally {
          isConversationLoading.value = false
        }
      } catch (error) {
        console.error('文件上传失败:', error)
        ElMessage.error('文件上传失败: ' + error.message)
        isConversationLoading.value = false
      }
    }
    
    // 获取媒体类型
    const getMediaType = (extension) => {
      if (['.jpg', '.jpeg', '.png', '.gif'].includes(extension)) {
        return 'image'
      } else if (['.mp3', '.wav', '.m4a'].includes(extension)) {
        return 'audio'
      } else if (['.mp4', '.mov', '.avi'].includes(extension)) {
        return 'video'
      }
      return 'document'
    }
    
    // 添加多模态消息发送方法，此方法只在服务器端使用，本地使用sendMultiModalMessageWithBase64
    // const sendMultiModalMessage = async (content, mediaType, mediaUrl) => {
    //   if (!mediaUrl) return
      
    //   // 添加临时消息，使用用户提供的内容
    //   const tempMessage = {
    //     id: 'temp_' + Date.now(),
    //     role: 'user',
    //     content: content || '', // 不再使用空格占位，使用空字符串
    //     media_type: mediaType,
    //     media_url: mediaUrl,
    //     isLoading: true,
    //     created_at: new Date().toISOString(),
    //     createdAt: new Date().toISOString(),
    //     conversationId: selectedConversationId.value
    //   }
      
    //   conversationMessages.value.push(tempMessage)
    //   isConversationLoading.value = true
      
    //   try {
    //     // 保存消息到本地数据库
    //     const userMessage = {
    //       id: uuidv4(),
    //       role: 'user',
    //       content: content || '', // 同样不使用空格占位
    //       media_type: mediaType,
    //       media_url: mediaUrl,
    //       created_at: new Date().toISOString(),
    //       createdAt: new Date().toISOString(),
    //       conversationId: selectedConversationId.value
    //     }
        
    //     // 替换临时消息
    //     const tempIndex = conversationMessages.value.findIndex(m => m.id === tempMessage.id)
    //     if (tempIndex >= 0) {
    //       conversationMessages.value[tempIndex] = userMessage
    //     }
        
    //     // 保存到本地数据库
    //     await saveMessageToDB(userMessage)
        
    //     // 更新对话最后修改时间
    //     const conversation = conversations.value.find(c => c.id === selectedConversationId.value)
    //     if (conversation) {
    //       conversation.updated_at = new Date().toISOString()
    //       conversation.updatedAt = new Date().toISOString()
    //       await saveConversationToDB(conversation)
    //     }
        
    //     // 构建API请求对象
    //     let recentMessages = conversationMessages.value.slice(-10)
        
    //     // 添加系统提示
    //     if (!recentMessages.some(msg => msg.role === 'system')) {
    //       recentMessages.unshift({
    //         role: 'system',
    //         content: '你是WordArt锦书AI助手，由通义千问大语言模型驱动。'
    //       })
    //     }
        
    //     const url = `/api/chat/completions`
        
    //     // 构建请求体
    //     let requestBody = {
    //       model: currentModel.value,
    //       messages: recentMessages.map(msg => {
    //         // 处理有媒体的消息
    //         if (msg.media_base64) {
    //           let content = [];
    //           const mediaFormat = fileExtension.substring(1); // 去掉前面的点
    //           const mimeType = getMimeType(mediaFormat);
              
    //           if (msg.media_type === 'image') {
    //             // 图片使用image_url类型
    //             content.push({
    //               "type": "image_url",
    //               "image_url": { 
    //                 "url": `data:${mimeType};base64,${msg.media_base64.split(',')[1]}`
    //               }
    //             });
    //           } else if (msg.media_type === 'audio') {
    //             // 音频使用input_audio类型 (根据官方文档)
    //             content.push({
    //               "type": "input_audio",
    //               "input_audio": { 
    //                 "data": `data:;base64,${msg.media_base64.split(',')[1]}`,
    //                 "format": mediaFormat
    //               }
    //             });
    //           } else if (msg.media_type === 'video') {
    //             // 视频使用video_url类型 (根据官方文档)
    //             content.push({
    //               "type": "video_url",
    //               "video_url": { 
    //                 "url": `data:;base64,${msg.media_base64.split(',')[1]}`
    //               }
    //             });
    //           }
              
    //           // 添加文本内容
    //           content.push({ "type": "text", "text": msg.content });
              
    //           return { "role": msg.role, "content": content };
    //         } else if (msg.media_url) {
    //           // 原来的URL处理逻辑
    //           let content = [];
              
    //           if (msg.media_type === 'image') {
    //             const absoluteUrl = msg.media_url.startsWith('http') 
    //               ? msg.media_url 
    //               : `${window.location.origin}${msg.media_url}`;
                
    //             console.log('图片原始URL:', msg.media_url);
    //             console.log('图片转换后绝对URL:', absoluteUrl);
                
    //             content.push({
    //               "type": "image_url",
    //               "image_url": { "url": absoluteUrl }
    //             });
    //           } else if (msg.media_type === 'audio') {
    //             const absoluteUrl = msg.media_url.startsWith('http') 
    //               ? msg.media_url 
    //               : `${window.location.origin}${msg.media_url}`;
                
    //             content.push({
    //               "type": "input_audio",
    //               "input_audio": { 
    //                 "data": absoluteUrl,
    //                 "format": msg.media_url.split('.').pop() || 'mp3'
    //               }
    //             });
    //           } else if (msg.media_type === 'video') {
    //             const absoluteUrl = msg.media_url.startsWith('http') 
    //               ? msg.media_url 
    //               : `${window.location.origin}${msg.media_url}`;
                
    //             content.push({
    //               "type": "video_url",
    //               "video_url": { "url": absoluteUrl }
    //             });
    //           }
              
    //           // 添加文本内容
    //           content.push({ "type": "text", "text": msg.content });
              
    //           return { "role": msg.role, "content": content };
    //         } else {
    //           // 普通文本消息
    //           return { "role": msg.role, "content": msg.content };
    //         }
    //       }),
    //       modalities: ["text"],
    //       stream: true,
    //       stream_options: { include_usage: true }
    //     }
        
    //     // 添加日志输出以便调试
    //     console.log('发送多模态请求:', JSON.stringify(requestBody))
        
    //     // 执行与sendMessage一样的API调用和响应处理逻辑
    //     const response = await fetchWithTimeout(url, {
    //       method: 'POST',
    //       headers: {
    //         'Content-Type': 'application/json',
    //         ...(isLoggedIn.value ? {
    //           'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
    //         } : {})
    //       },
    //       body: JSON.stringify(requestBody),
    //     }, 120000) // Omni模型使用120秒超时
        
    //     // 处理响应和错误，与sendMessage方法中相同
    //     if (!response.ok) {
    //       console.error('API请求失败:', response.status, response.statusText)
    //       throw new Error(`Omni模型请求失败: ${response.status} ${response.statusText}`)
    //     }
        
    //     // 处理流式响应
    //     const reader = response.body.getReader()
    //     const decoder = new TextDecoder()
    //     let aiResponse = ''
    //     let aiMessageId = ''
        
    //     // 删除临时消息
    //     conversationMessages.value.pop()
        
    //     try {
    //       while (true) {
    //         const { done, value } = await reader.read()
    //         if (done) break
            
    //         const chunk = decoder.decode(value)
    //         const lines = chunk.split('\n').filter(line => line.trim() !== '')
            
    //         for (const line of lines) {
    //           if (line.startsWith('data: ')) {
    //             const data = line.substring(6)
    //             if (data === '[DONE]') continue
                
    //             try {
    //               const parsed = JSON.parse(data)
                  
    //               // 处理错误响应
    //               if (parsed.error) {
    //                 throw new Error(parsed.message || 'AI生成回复失败')
    //               }
                  
    //               if (!aiMessageId && parsed.id) {
    //                 aiMessageId = parsed.id
    //               }
                  
    //               // 处理Omni模型的特殊响应格式
    //               if (parsed.choices && parsed.choices[0]) {
    //                 const delta = parsed.choices[0].delta
    //                 if (delta && delta.content) {
    //                   aiResponse += delta.content
                      
    //                   // 更新或添加AI消息
    //                   const existingMsgIndex = conversationMessages.value.findIndex(m => m.id === aiMessageId)
                      
    //                   if (existingMsgIndex >= 0) {
    //                     conversationMessages.value[existingMsgIndex].content = aiResponse
    //                   } else {
    //                     conversationMessages.value.push({
    //                       id: aiMessageId,
    //                       role: 'assistant',
    //                       content: aiResponse,
    //                       created_at: new Date().toISOString(),
    //                       createdAt: new Date().toISOString(),
    //                       conversationId: selectedConversationId.value
    //                     })
    //                   }
    //                 }
    //               }
    //             } catch (err) {
    //               console.error('解析流数据错误:', err, data)
    //               throw err
    //             }
    //           }
    //         }
    //       }
    //     } catch (error) {
    //       console.error('读取流响应错误:', error)
    //       // 如果在接收流过程中发生错误，但已经有部分响应，不抛出错误
    //       if (!aiResponse) {
    //         throw error
    //       }
    //     } finally {
    //       // 确保AI消息被添加并保存
    //       if (aiResponse) {
    //         const finalAiMessage = {
    //           id: aiMessageId || 'ai_' + Date.now(),
    //           role: 'assistant',
    //           content: aiResponse,
    //           created_at: new Date().toISOString(),
    //           createdAt: new Date().toISOString(),
    //           conversationId: selectedConversationId.value
    //         }
            
    //         // 检查是否已存在此消息
    //         const existingMsgIndex = conversationMessages.value.findIndex(m => m.id === finalAiMessage.id)
    //         if (existingMsgIndex >= 0) {
    //           conversationMessages.value[existingMsgIndex] = finalAiMessage
    //         } else {
    //           conversationMessages.value.push(finalAiMessage)
    //         }
            
    //         // 保存到本地数据库
    //         await saveMessageToDB(finalAiMessage)
            
    //         // 更新对话最后修改时间
    //         const conversation = conversations.value.find(c => c.id === selectedConversationId.value)
    //         if (conversation) {
    //           conversation.updated_at = new Date().toISOString()
    //           conversation.updatedAt = new Date().toISOString()
    //           await saveConversationToDB(conversation)
    //         }
    //       }
    //     }
    //   } catch (error) {
    //     console.error('发送多模态消息错误:', error)
        
    //     // 移除临时消息
    //     const tempIndex = conversationMessages.value.findIndex(m => m.id === tempMessage.id)
    //     if (tempIndex >= 0) {
    //       conversationMessages.value.splice(tempIndex, 1)
    //     }
        
    //     // 添加错误消息
    //     conversationMessages.value.push({
    //       id: 'error_' + Date.now(),
    //       role: 'system',
    //       content: `发送失败: ${error.message}. 请重试或检查网络连接。`,
    //       created_at: new Date().toISOString(),
    //       createdAt: new Date().toISOString(),
    //       conversationId: selectedConversationId.value,
    //       error: true
    //     })
    //   } finally {
    //     isConversationLoading.value = false
    //   }
    // }
    
    // 添加读取文件为Base64的辅助函数
    const readFileAsBase64 = (file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    };

    // 判断是否为图片文件
    const isImageFile = (extension) => {
      return ['.jpg', '.jpeg', '.png', '.gif'].includes(extension);
    };

    // 判断是否为音频文件
    const isAudioFile = (extension) => {
      return ['.mp3', '.wav', '.m4a'].includes(extension);
    };

    // 判断是否为视频文件
    const isVideoFile = (extension) => {
      return ['.mp4', '.mov', '.avi'].includes(extension);
    };

    // 发送带Base64数据的多模态消息
    
    const sendMultiModalMessageWithBase64 = async (content, mediaType, base64Data, fileExtension) => {
      if (!base64Data) return;
      
      // 添加临时消息
      const tempMessage = {
        id: 'temp_' + Date.now(),
        role: 'user',
        content: content || ' ', // 恢复使用空格占位
        media_type: mediaType,
        media_base64: base64Data,
        isLoading: true,
        created_at: new Date().toISOString(),
        createdAt: new Date().toISOString(),
        conversationId: selectedConversationId.value
      };
      
      conversationMessages.value.push(tempMessage);
      console.log('Added temp message to conversationMessages:', JSON.stringify(conversationMessages.value[conversationMessages.value.length - 1])); // <-- 添加日志
      isConversationLoading.value = true;
      
      try {
        // 保存消息到本地数据库
        const userMessage = {
          id: uuidv4(),
          role: 'user',
          content: content || ' ', // 恢复使用空格占位
          media_type: mediaType,
          media_base64: base64Data,
          created_at: new Date().toISOString(),
          createdAt: new Date().toISOString(),
          conversationId: selectedConversationId.value
        };
        
        // 替换临时消息
        const tempIndex = conversationMessages.value.findIndex(m => m.id === tempMessage.id)
        if (tempIndex >= 0) {
          conversationMessages.value[tempIndex] = userMessage
        }
        
        // 保存到本地数据库
        await saveMessageToDB(userMessage)
        
        // 更新对话最后修改时间
        const conversation = conversations.value.find(c => c.id === selectedConversationId.value)
        if (conversation) {
          conversation.updated_at = new Date().toISOString()
          conversation.updatedAt = new Date().toISOString()
          await saveConversationToDB(conversation)
        }
        
        // 构建API请求对象
        let recentMessages = conversationMessages.value.slice(-10)
        
        // 添加系统提示
        if (!recentMessages.some(msg => msg.role === 'system')) {
          recentMessages.unshift({
            role: 'system',
            content: '你是WordArt锦书AI助手，由通义千问大语言模型驱动。'
          })
        }
        
        const url = `/api/chat/completions`
        
        // 构建请求体
        let requestBody = {
          model: currentModel.value,
          messages: recentMessages.map(msg => {
            // 处理有媒体的消息
            if (msg.media_base64) {
              let content = [];
              const mediaFormat = fileExtension.substring(1); // 去掉前面的点
              const mimeType = getMimeType(mediaFormat);
              
              if (msg.media_type === 'image') {
                // 图片使用image_url类型
                content.push({
                  "type": "image_url",
                  "image_url": { 
                    "url": `data:${mimeType};base64,${msg.media_base64.split(',')[1]}`
                  }
                });
              } else if (msg.media_type === 'audio') {
                // 音频使用input_audio类型 (根据官方文档)
                content.push({
                  "type": "input_audio",
                  "input_audio": { 
                    "data": `data:;base64,${msg.media_base64.split(',')[1]}`,
                    "format": mediaFormat
                  }
                });
              } else if (msg.media_type === 'video') {
                // 视频使用video_url类型 (根据官方文档)
                content.push({
                  "type": "video_url",
                  "video_url": { 
                    "url": `data:;base64,${msg.media_base64.split(',')[1]}`
                  }
                });
              }
              
              // 添加文本内容
              content.push({ "type": "text", "text": msg.content });
              
              return { "role": msg.role, "content": content };
            } else if (msg.media_url) {
              // 原来的URL处理逻辑
              let content = [];
              
              if (msg.media_type === 'image') {
                const absoluteUrl = msg.media_url.startsWith('http') 
                  ? msg.media_url 
                  : `${window.location.origin}${msg.media_url}`;
                
                console.log('图片原始URL:', msg.media_url);
                console.log('图片转换后绝对URL:', absoluteUrl);
                
                content.push({
                  "type": "image_url",
                  "image_url": { "url": absoluteUrl }
                });
              } else if (msg.media_type === 'audio') {
                const absoluteUrl = msg.media_url.startsWith('http') 
                  ? msg.media_url 
                  : `${window.location.origin}${msg.media_url}`;
                
                content.push({
                  "type": "input_audio",
                  "input_audio": { 
                    "data": absoluteUrl,
                    "format": msg.media_url.split('.').pop() || 'mp3'
                  }
                });
              } else if (msg.media_type === 'video') {
                const absoluteUrl = msg.media_url.startsWith('http') 
                  ? msg.media_url 
                  : `${window.location.origin}${msg.media_url}`;
                
                content.push({
                  "type": "video_url",
                  "video_url": { "url": absoluteUrl }
                });
              }
              
              // 添加文本内容
              content.push({ "type": "text", "text": msg.content });
              
              return { "role": msg.role, "content": content };
            } else {
              // 普通文本消息
              return { "role": msg.role, "content": msg.content };
            }
          }),
          modalities: ["text"],
          stream: true,
          stream_options: { include_usage: true }
        }
        
        // 添加日志输出以便调试
        console.log('发送多模态请求:');
        console.log('模型:', requestBody.model);
        console.log('消息数量:', requestBody.messages.length);
        console.log('第一条消息类型:', requestBody.messages[0].role);
        console.log('最后一条消息类型:', requestBody.messages[requestBody.messages.length-1].role);
        
        // 执行与sendMessage一样的API调用和响应处理逻辑
        const response = await fetchWithTimeout(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(isLoggedIn.value ? {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            } : {})
          },
          body: JSON.stringify(requestBody),
        }, 120000); // Omni模型使用120秒超时
        
        // 处理响应和错误，与sendMessage方法中相同
        if (!response.ok) {
          console.error('API请求失败:', response.status, response.statusText)
          throw new Error(`Omni模型请求失败: ${response.status} ${response.statusText}`)
        }
        
        // 处理流式响应
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let aiResponse = ''
        let aiMessageId = ''
        
        // 删除临时消息
        //conversationMessages.value.pop() // 删除临时消息
        
        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break
            
            const chunk = decoder.decode(value)
            const lines = chunk.split('\n').filter(line => line.trim() !== '')
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.substring(6)
                if (data === '[DONE]') continue
                
                try {
                  const parsed = JSON.parse(data)
                  
                  // 处理错误响应
                  if (parsed.error) {
                    throw new Error(parsed.message || 'AI生成回复失败')
                  }
                  
                  if (!aiMessageId && parsed.id) {
                    aiMessageId = parsed.id
                  }
                  
                  // 处理Omni模型的特殊响应格式
                  if (parsed.choices && parsed.choices[0]) {
                    const delta = parsed.choices[0].delta
                    if (delta && delta.content) {
                      aiResponse += delta.content
                      
                      // 更新或添加AI消息
                      const existingMsgIndex = conversationMessages.value.findIndex(m => m.id === aiMessageId)
                      
                      if (existingMsgIndex >= 0) {
                        conversationMessages.value[existingMsgIndex].content = aiResponse
                      } else {
                        conversationMessages.value.push({
                          id: aiMessageId,
                          role: 'assistant',
                          content: aiResponse,
                          created_at: new Date().toISOString(),
                          createdAt: new Date().toISOString(),
                          conversationId: selectedConversationId.value
                        })
                      }
                    }
                  }
                } catch (err) {
                  console.error('解析流数据错误:', err, data)
                  throw err
                }
              }
            }
          }
        } catch (error) {
          console.error('读取流响应错误:', error)
          // 如果在接收流过程中发生错误，但已经有部分响应，不抛出错误
          if (!aiResponse) {
            throw error
          }
        } finally {
          // 确保AI消息被添加并保存
          if (aiResponse) {
            const finalAiMessage = {
              id: aiMessageId || 'ai_' + Date.now(),
              role: 'assistant',
              content: aiResponse,
              created_at: new Date().toISOString(),
              createdAt: new Date().toISOString(),
              conversationId: selectedConversationId.value
            }
            
            // 检查是否已存在此消息
            const existingMsgIndex = conversationMessages.value.findIndex(m => m.id === finalAiMessage.id)
            if (existingMsgIndex >= 0) {
              conversationMessages.value[existingMsgIndex] = finalAiMessage
            } else {
              conversationMessages.value.push(finalAiMessage)
            }
            
            // 保存到本地数据库
            await saveMessageToDB(finalAiMessage)
            
            // 更新对话最后修改时间
            const conversation = conversations.value.find(c => c.id === selectedConversationId.value)
            if (conversation) {
              conversation.updated_at = new Date().toISOString()
              conversation.updatedAt = new Date().toISOString()
              await saveConversationToDB(conversation)
            }
          }
        }
      } catch (error) {
        console.error('发送多模态消息错误:', error)
        
        // 移除临时消息
        const tempIndex = conversationMessages.value.findIndex(m => m.id === tempMessage.id)
        if (tempIndex >= 0) {
          conversationMessages.value.splice(tempIndex, 1)
        }
        
        // 添加错误消息
        conversationMessages.value.push({
          id: 'error_' + Date.now(),
          role: 'system',
          content: `发送失败: ${error.message}. 请重试或检查网络连接。`,
          created_at: new Date().toISOString(),
          createdAt: new Date().toISOString(),
          conversationId: selectedConversationId.value,
          error: true
        })
      } finally {
        isConversationLoading.value = false
      }
    }
    // 模型相关方法
    const handleModelChange = (modelId) => {
      currentModel.value = modelId
      
      // 如果有活跃对话且用户已登录，更新会话的模型
      if (selectedConversationId.value && isLoggedIn.value) {
        updateConversationModel(selectedConversationId.value, modelId)
      }
    }
    
    const updateConversationModel = async (conversationId, modelId) => {
      try {
        await authFetch(`/api/chat/conversations/${conversationId}`, {
          method: 'PATCH',
          body: JSON.stringify({ model: modelId })
        })
      } catch (error) {
        console.error('更新对话模型失败:', error)
        // 这里我们不显示错误消息，因为这不是关键操作
      }
    }
    
    // 添加滚动到底部的方法
    const scrollToBottom = () => {
      if (messageListRef.value) {
        nextTick(() => {
          const container = messageListRef.value.$el
          if (container) {
            container.scrollTop = container.scrollHeight
          }
        })
      }
    }

    // 监听消息列表变化，自动滚动
    watch(conversationMessages, () => {
      scrollToBottom()
    }, { deep: true })

    // 计算当前模型的能力
    const currentModelCapabilities = computed(() => {
      const model = availableModels.value.find(m => m.id === currentModel.value)
      return model ? model.capabilities : []
    })
    
    // 计算当前模型名称
    const currentModelName = computed(() => {
      const model = availableModels.value.find(m => m.id === currentModel.value)
      return model ? model.name : '选择模型'
    })

    // 计算当前模型类型
    const currentModelType = computed(() => {
      const model = availableModels.value.find(m => m.id === currentModel.value)
      return model?.capabilities.includes('image') ? '多模态' : '仅文本'
    })
    
    // 监听模型变化
    watch(currentModel, (newModel) => {
      handleModelChange(newModel)
    })

    // 初始化用户状态
    const initUserState = () => {
      if (isAuthenticated()) {
        isLoggedIn.value = true
        currentUser.value = getCurrentUser()
        // 加载用户的对话列表
        fetchUserConversations()
      } else {
        isLoggedIn.value = false
        currentUser.value = null
      }
    }

    // 在组件挂载时初始化用户状态
    onMounted(() => {
      initUserState()
    })

    // 初始化
    onMounted(async () => {
      console.log('ChatView 已挂载');
      
      try {
        // 初始化数据库
        await initDatabase();
        console.log('数据库初始化完成');
        
        // 不再尝试从服务器获取数据，始终使用本地数据库
        console.log('始终从本地数据库加载对话');
        conversations.value = await loadConversationsFromDB();
        
        // 如果有对话，选择第一个；否则准备创建新对话
        if (conversations.value.length > 0) {
          console.log('选择第一个对话:', conversations.value[0].id);
          selectedConversationId.value = conversations.value[0].id;
          // 直接从本地加载消息，不发送API请求
          conversationMessages.value = await loadMessagesFromDB(selectedConversationId.value);
        } else {
          console.log('没有现有对话，准备创建新对话');
          selectedConversationId.value = null;
          conversationMessages.value = [];
          // 自动创建新对话
          await handleNewConversation();
        }
      } catch (error) {
        console.error('ChatView 初始化失败:', error);
        ElMessage.error('初始化失败: ' + (error.message || '未知错误'));
      } finally {
        isConversationLoading.value = false;
      }
    });
    
    // 初始化数据库
    const initDatabase = () => {
      return new Promise((resolve, reject) => {
        try {
          // 创建数据库
          const request = window.indexedDB.open('WordArtChat', 1)
          
          request.onerror = (event) => {
            console.error('初始化数据库失败:', event)
            reject(new Error('初始化数据库失败'))
          }
          
          // 数据库第一次创建或升级版本时，创建存储对象
          request.onupgradeneeded = (event) => {
            console.log('创建/升级数据库...')
            const db = event.target.result
            
            // 创建对话表
            if (!db.objectStoreNames.contains('conversations')) {
              const conversationStore = db.createObjectStore('conversations', { keyPath: 'id' })
              conversationStore.createIndex('updatedAt', 'updatedAt', { unique: false })
            }
            
            // 创建消息表
            if (!db.objectStoreNames.contains('messages')) {
              const messageStore = db.createObjectStore('messages', { keyPath: 'id' })
              messageStore.createIndex('conversationId', 'conversationId', { unique: false })
              messageStore.createIndex('createdAt', 'createdAt', { unique: false })
            }
          }
          
          request.onsuccess = (event) => {
            const db = event.target.result
            console.log('数据库初始化成功:', db.name, 'v', db.version)
            resolve(db)
          }
        } catch (error) {
          console.error('初始化数据库出错:', error)
          reject(error)
        }
      })
    }

    // 从数据库加载对话列表
    const loadConversationsFromDB = async () => {
      try {
        const db = await initDatabase()
        return new Promise((resolve, reject) => {
          const transaction = db.transaction(['conversations'], 'readonly')
          const store = transaction.objectStore('conversations')
          const request = store.getAll()
          
          request.onsuccess = () => {
            resolve(request.result || [])
          }
          
          request.onerror = (event) => {
            console.error('加载对话列表失败:', event)
            reject(new Error('加载对话列表失败'))
          }
        })
      } catch (error) {
        console.error('从数据库加载对话失败:', error)
        return []
      }
    }

    // 从数据库加载特定对话的消息
    const loadMessagesFromDB = async (conversationId) => {
      try {
        const db = await initDatabase()
        return new Promise((resolve, reject) => {
          const transaction = db.transaction(['messages'], 'readonly')
          const store = transaction.objectStore('messages')
          const index = store.index('conversationId')
          const request = index.getAll(IDBKeyRange.only(conversationId))
          
          request.onsuccess = () => {
            // 按时间排序
            const messages = request.result || []
            messages.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
            resolve(messages)
          }
          
          request.onerror = (event) => {
            console.error('加载消息失败:', event)
            reject(new Error('加载消息失败'))
          }
        })
      } catch (error) {
        console.error('从数据库加载消息失败:', error)
        return []
      }
    }

    // 修改saveConversationToDB方法，确保对象可以被序列化
    const saveConversationToDB = async (conversation) => {
      try {
        const db = await initDatabase();
        return new Promise((resolve, reject) => {
          const transaction = db.transaction(['conversations'], 'readwrite');
          const store = transaction.objectStore('conversations');
          
          // 创建可序列化的对象副本，避免可能包含无法克隆的属性
          const serializableConversation = {
            id: conversation.id,
            title: conversation.title || '新对话',
            model: conversation.model || 'qwen-max-latest',
            created_at: conversation.created_at || new Date().toISOString(),
            updated_at: conversation.updated_at || new Date().toISOString(),
            updatedAt: conversation.updatedAt || conversation.updated_at || new Date().toISOString()
          };
          
          const request = store.put(serializableConversation);
          
          request.onsuccess = () => {
            resolve(true);
          };
          
          request.onerror = (event) => {
            console.error('保存对话失败:', event);
            reject(new Error('保存对话失败'));
          };
        });
      } catch (error) {
        console.error('保存对话到数据库失败:', error);
        return false;
      }
    };

    // 修改saveMessageToDB方法，确保对象可以序列化
    const saveMessageToDB = async (message) => {
      try {
        const db = await initDatabase();
        return new Promise((resolve, reject) => {
          const transaction = db.transaction(['messages'], 'readwrite');
          const store = transaction.objectStore('messages');
          
          // 创建可序列化的对象副本，确保包含媒体字段
          const serializableMessage = {
            id: message.id,
            role: message.role,
            content: message.content,
            created_at: message.created_at || new Date().toISOString(),
            createdAt: message.createdAt || message.created_at || new Date().toISOString(),
            conversationId: message.conversationId,
            error: message.error || false,
            // 添加媒体字段
            media_type: message.media_type || null, 
            media_base64: message.media_base64 || null,
            media_url: message.media_url || null,
            // 添加多文件信息字段
            files_info: message.files_info || null 
          };
          
          // 如果 media_base64 过大，考虑不直接存储（可选优化）
          // if (serializableMessage.media_base64 && serializableMessage.media_base64.length > 1024 * 1024) { 
          //   console.warn("Base64 data is large, consider alternative storage or not storing directly.");
          //   // serializableMessage.media_base64 = null; // 例如，选择不存储
          // }

          const request = store.put(serializableMessage);
          
          request.onsuccess = () => {
            resolve(true);
          };
          
          request.onerror = (event) => {
            console.error('保存消息失败:', event);
            reject(new Error('保存消息失败'));
          };
        });
      } catch (error) {
        console.error('保存消息到数据库失败:', error);
        return false;
      }
    };

    // 删除对话及其消息
    const deleteConversationFromDB = async (conversationId) => {
      try {
        const db = await initDatabase()
        // 先删除对话下的所有消息
        await new Promise((resolve, reject) => {
          const transaction = db.transaction(['messages'], 'readwrite')
          const store = transaction.objectStore('messages')
          const index = store.index('conversationId')
          const request = index.openCursor(IDBKeyRange.only(conversationId))
          
          request.onsuccess = (event) => {
            const cursor = event.target.result
            if (cursor) {
              cursor.delete()
              cursor.continue()
            } else {
              resolve()
            }
          }
          
          request.onerror = (event) => {
            console.error('删除消息失败:', event)
            reject(new Error('删除消息失败'))
          }
        })
        
        // 再删除对话
        return new Promise((resolve, reject) => {
          const transaction = db.transaction(['conversations'], 'readwrite')
          const store = transaction.objectStore('conversations')
          const request = store.delete(conversationId)
          
          request.onsuccess = () => {
            resolve(true)
          }
          
          request.onerror = (event) => {
            console.error('删除对话失败:', event)
            reject(new Error('删除对话失败'))
          }
        })
      } catch (error) {
        console.error('从数据库删除对话失败:', error)
        return false
      }
    }

    // 添加删除对话的方法
    const deleteConversation = async (conversationId) => {
      try {
        if (!conversationId) return;
        
        // 从内存中删除
        const index = conversations.value.findIndex(c => c.id === conversationId);
        if (index >= 0) {
          conversations.value.splice(index, 1);
        }
        
        // 从数据库中删除对话及其消息
        await deleteConversationFromDB(conversationId);
        
        // 如果删除的是当前选中的对话，则切换到其他对话
        if (selectedConversationId.value === conversationId) {
          if (conversations.value.length > 0) {
            // 选择列表中的第一个对话
            await handleSelectConversation(conversations.value[0].id);
          } else {
            // 如果没有对话了，创建新对话
            selectedConversationId.value = null;
            conversationMessages.value = [];
            await handleNewConversation();
          }
        }
        
        ElMessage.success('对话已删除');
      } catch (error) {
        console.error('删除对话失败:', error);
        ElMessage.error('删除对话失败: ' + error.message);
      }
    };

    // 处理多文件上传
    const handleMultiFileUpload = async (files, userMessage = '') => {
      if (!files || files.length === 0) return;
      
      try {
        isConversationLoading.value = true;
        
        console.log(`准备上传${files.length}个文件`);
        
        // 创建FormData
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
          formData.append('files', files[i]);
        }
        
        // 发送上传请求
        const uploadResponse = await fetch('/api/chat/upload-multiple', {
          method: 'POST',
          headers: isLoggedIn.value ? {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          } : {},
          body: formData
        });
        
        if (!uploadResponse.ok) {
          const errorText = await uploadResponse.text();
          console.error('多文件上传失败:', errorText);
          ElMessage.error(`文件上传失败: ${errorText}`);
          isConversationLoading.value = false;
          return;
        }
        
        // 解析上传结果
        const uploadData = await uploadResponse.json();
        console.log('多文件上传结果:', uploadData);
        
        if (!uploadData.urls || uploadData.urls.length === 0) {
          ElMessage.error('文件上传成功但未返回URL');
          isConversationLoading.value = false;
          return;
        }
        
        // 构建富文本消息内容
        let messageContent = userMessage || '';
        let mediaType = null;
        let mediaUrl = null;
        
        // 选择第一个文件作为主要媒体类型和URL
        if (uploadData.urls.length > 0) {
          const firstFile = uploadData.urls[0];
          const fileExtension = firstFile.url.slice(firstFile.url.lastIndexOf('.')).toLowerCase();
          mediaType = getMediaType(fileExtension);
          mediaUrl = firstFile.url;
        }
        
        // 构建包含所有文件链接的消息
        let fullMessageContent = messageContent;
        
        // 添加文件链接
        if (uploadData.urls.length > 0) {
          if (fullMessageContent) fullMessageContent += '\n\n';
          fullMessageContent += `上传了${uploadData.urls.length}个文件:\n`;
          
          for (const fileInfo of uploadData.urls) {
            const fileName = fileInfo.filename || fileInfo.url.split('/').pop();
            const fileUrl = fileInfo.url;
            
            // 根据文件类型添加不同的格式
            const fileExtension = fileUrl.slice(fileUrl.lastIndexOf('.')).toLowerCase();
            const fileMediaType = getMediaType(fileExtension);
            
            if (fileMediaType === 'image') {
              // 图片使用markdown格式
              fullMessageContent += `\n![${fileName}](${fileUrl})`;
            } else {
              // 其他文件用链接
              fullMessageContent += `\n[${fileName}](${fileUrl})`;
            }
          }
        }
        
        // 移除添加临时消息的代码，直接使用sendMultiModalMessage
        await sendMultiModalMessage(fullMessageContent, mediaType, mediaUrl);
        
        ElMessage.success(`成功上传了${uploadData.urls.length}个文件`);
        
      } catch (error) {
        console.error('多文件上传处理错误:', error);
        ElMessage.error('文件处理失败: ' + error.message);
      } finally {
        isConversationLoading.value = false;
      }
    };
    

    



    // 获取文件MIME类型
    const getMimeType = (format) => {
      const mimeTypes = {
        // 图片类型
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        // 音频类型
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'm4a': 'audio/m4a',
        // 视频类型
        'mp4': 'video/mp4',
        'mov': 'video/quicktime',
        'avi': 'video/x-msvideo'
      };
      
      return mimeTypes[format] || `application/${format}`;
    };

    // 新增：处理多图片发送 (使用Base64)
    const handleSendMultiImages = async ({ files, message: userMessage }) => {
      console.log(`[MultiImages] Received ${files.length} images to send with message: "${userMessage}"`);
      if (!files || files.length === 0) return;
      
      // 再次验证数量和类型 (防御性编程)
      if (files.length > 10) {
        ElMessage.error('一次最多只能上传 10 张图片。');
        return;
      }
      const allImages = files.every(f => 
          ['.jpg', '.jpeg', '.png', '.gif'].includes('.' + f.name.split('.').pop().toLowerCase())
      );
      if (!allImages) {
        ElMessage.error('多文件上传仅支持图片。');
        return;
      }
      
      isConversationLoading.value = true;
      let tempUserMessageId = 'temp_multi_' + Date.now();
      let base64DataUrls = [];
      let fileInfos = files.map(f => ({ name: f.name, type: f.type, size: f.size })); // 用于临时消息显示
      
      // 添加临时用户消息 (只显示文本和文件信息)
      conversationMessages.value.push({
        id: tempUserMessageId,
        role: 'user',
        content: userMessage || ' ', // 确保有内容
        media_type: 'image', // 标记为图片类型
        files_info: fileInfos, // 存储文件信息用于显示
        isLoading: true,
        created_at: new Date().toISOString(),
        createdAt: new Date().toISOString(),
        conversationId: selectedConversationId.value
      });
      
      try {
        // 1. 将所有图片文件转为 Base64 Data URL
        const base64Promises = files.map(file => readFileAsBase64(file));
        base64DataUrls = await Promise.all(base64Promises);
        console.log(`[MultiImages] Successfully converted ${base64DataUrls.length} images to Base64.`);
        
        // 2. 准备发送给 AI API 的消息
        //    需要构建一个包含文本和多个图片内容块的 message 对象
        const userMessageForApi = {
            role: 'user',
            content: [] // content 是一个数组
        };
        
        // 添加图片内容块
        base64DataUrls.forEach(dataUrl => {
            userMessageForApi.content.push({
                type: 'image_url',
                image_url: { url: dataUrl } // 直接使用 Data URL
            });
        });
        
        // 添加文本内容块
        userMessageForApi.content.push({
            type: 'text',
            text: userMessage || ' ' // 确保有文本，即使是空字符串或空格
        });
        
        // 3. 保存这个组合消息到数据库 (只保存文本和文件信息，不存Base64)
        const finalUserMessage = {
            id: uuidv4(),
            role: 'user',
            content: userMessage || ' ',
            media_type: 'image_multi', // 使用特殊类型标记多图片
            files_info: fileInfos, // 保存文件信息
            created_at: new Date().toISOString(),
            createdAt: new Date().toISOString(),
            conversationId: selectedConversationId.value
        };
        
        // 替换临时消息
        const tempIndex = conversationMessages.value.findIndex(m => m.id === tempUserMessageId);
        if (tempIndex >= 0) {
            conversationMessages.value[tempIndex] = finalUserMessage;
            conversationMessages.value[tempIndex].isLoading = false; // 移除加载状态
        }
        await saveMessageToDB(finalUserMessage);
        
        // 更新对话更新时间
        const conversation = conversations.value.find(c => c.id === selectedConversationId.value);
        if (conversation) {
          conversation.updated_at = new Date().toISOString();
          conversation.updatedAt = new Date().toISOString();
          await saveConversationToDB(conversation);
        }
        
        // 4. 构建发送到 /api/chat/completions 的请求体
        let recentMessages = conversationMessages.value
            .filter(msg => msg.id !== finalUserMessage.id) // 排除刚保存的聚合消息
            .slice(-9); // 取最近的9条历史消息 + 1条新消息 = 10条上下文
            
        // 添加系统提示 (如果需要)
        if (!recentMessages.some(msg => msg.role === 'system')) {
          recentMessages.unshift({
            role: 'system',
            content: '你是WordArt锦书AI助手，由通义千问大语言模型驱动。'
          });
        }
        
        // 将新的多模态消息添加到请求的消息列表末尾
        recentMessages.push(userMessageForApi);
        
        
        const mappedMessages = recentMessages.map(msg => {
           // --- FIX: Add checks and filtering ---
           if (!msg || typeof msg !== 'object') {
               console.warn("[MultiImages] Skipping invalid item in recentMessages:", msg);
               return null; // Return null for invalid items
           }
           // --- FIX END ---
           
           // 处理历史消息中的媒体 (如果之前保存了 Base64 或 URL)
           if (msg.media_base64) {
               let content = [];
               // --- FIX START ---
               let mediaFormat = 'unknown';
               if (msg.media_type === 'image') {
                   // 尝试从 files_info 获取 (新多图片或未来可能的单文件带info)
                   if (msg.files_info && msg.files_info[0] && msg.files_info[0].name) {
                       mediaFormat = msg.files_info[0].name.split('.').pop() || 'png';
                   } else {
                       // 回退：旧的单文件消息没有 files_info，根据类型默认
                       mediaFormat = 'png'; 
                       console.warn("历史消息(Base64)缺少files_info，图片格式默认设为png");
                   }
               } else if (msg.media_type === 'audio') {
                   // 对于音频也添加类似的回退
                   if (msg.files_info && msg.files_info[0] && msg.files_info[0].name) {
                       mediaFormat = msg.files_info[0].name.split('.').pop() || 'mp3';
                   } else {
                       mediaFormat = 'mp3'; // 默认音频格式
                       console.warn("历史消息(Base64)缺少files_info，音频格式默认设为mp3");
                   }
               } else if (msg.media_type === 'video') {
                   // 对于视频的回退
                   if (msg.files_info && msg.files_info[0] && msg.files_info[0].name) {
                       mediaFormat = msg.files_info[0].name.split('.').pop() || 'mp4';
                   } else {
                       mediaFormat = 'mp4'; // 默认视频格式
                       console.warn("历史消息(Base64)缺少files_info，视频格式默认设为mp4");
                   }
               }
               // --- FIX END ---
               
               const mimeType = getMimeType(mediaFormat);
               
               // 根据修正后的 media_type 和 format 构造 content
               if (msg.media_type === 'image') {
                   content.push({
                       type: "image_url",
                       image_url: { url: `data:${mimeType};base64,${msg.media_base64.split(',')[1]}` }
                   });
               } else if (msg.media_type === 'audio') {
                   content.push({
                       type: "input_audio",
                       input_audio: { 
                           data: `data:${mimeType};base64,${msg.media_base64.split(',')[1]}`, 
                           format: mediaFormat 
                       }
                   });
               } else if (msg.media_type === 'video') {
                   content.push({
                       type: "video_url",
                       video_url: { url: `data:${mimeType};base64,${msg.media_base64.split(',')[1]}` }
                   });
               }
               
               // 添加文本部分
               content.push({ type: "text", text: msg.content || ' ' }); // 确保有text部分
               return { role: msg.role, content: content };
           } 
           // 处理新添加的多模态消息（已经是正确格式）
           else if (msg.role === 'user' && Array.isArray(msg.content)) {
               return msg;
           } 
           // 其他普通文本消息
           else if (msg.role && msg.content !== undefined && msg.content !== null && typeof msg.content === 'string') { // 确保是字符串
               return { role: msg.role, content: msg.content };
           } else {
               console.warn("[MultiImages] Skipping message with unexpected format or missing role/content:", msg);
               return null; // Return null for invalid format
           }
        }); // <-- map 结束
        


        const finalMessages = mappedMessages.filter(Boolean); // <-- filter 执行



        const requestBody = {
          model: currentModel.value,
          messages: finalMessages, 
          // modalities: ["text"], // 移除
          stream: true,
          stream_options: { include_usage: true }
        };


        // 5. 发送请求并处理响应 (与 sendMultiModalMessageWithBase64 类似)
        const url = `/api/chat/completions`;
        const response = await fetchWithTimeout(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(isLoggedIn.value ? {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            } : {})
          },
          body: JSON.stringify(requestBody),
        }, 120000); // 使用较长超时

        if (!response.ok) {
          console.error('API请求失败 (多图片):', response.status, response.statusText);
          const errorText = await response.text();
          throw new Error(`多图片消息请求失败: ${response.status} ${response.statusText} - ${errorText}`);
        }

        // 处理流式响应 (与 sendMultiModalMessageWithBase64 基本相同)
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let aiResponse = '';
        let aiMessageId = '';
        let assistantMessageAdded = false;

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n').filter(line => line.trim() !== '');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.substring(6);
                if (data === '[DONE]') continue;
                
                try {
                  const parsed = JSON.parse(data);
                  if (parsed.error) {
                    throw new Error(parsed.message || 'AI生成回复失败 (多图片)');
                  }
                  
                  if (!aiMessageId && parsed.id) {
                    aiMessageId = parsed.id;
                  }
                  
                  if (parsed.choices && parsed.choices[0]) {
                    const delta = parsed.choices[0].delta;
                    if (delta && delta.content) {
                      aiResponse += delta.content;
                      
                      const existingMsgIndex = conversationMessages.value.findIndex(m => m.id === aiMessageId);
                      if (existingMsgIndex >= 0) {
                        conversationMessages.value[existingMsgIndex].content = aiResponse;
                      } else if (!assistantMessageAdded) {
                          const newAssistantMessage = {
                              id: aiMessageId || 'ai_multi_' + Date.now(),
                              role: 'assistant',
                              content: aiResponse,
                              created_at: new Date().toISOString(),
                              createdAt: new Date().toISOString(),
                              conversationId: selectedConversationId.value
                          };
                          conversationMessages.value.push(newAssistantMessage);
                          assistantMessageAdded = true; // 标记已添加
                      }
                    }
                  }
                } catch (err) {
                  console.error('解析流数据错误 (多图片):', err, data);
                  // 不轻易抛出错误，让流程继续
                }
              }
            }
          }
        } catch (error) {
          console.error('读取流响应错误 (多图片):', error);
          // 如果出错时还没有AI响应，则抛出
          if (!aiResponse) throw error; 
        } finally {
          if (aiResponse && aiMessageId) {
            const finalAiMessage = {
              id: aiMessageId,
              role: 'assistant',
              content: aiResponse,
              created_at: new Date().toISOString(),
              createdAt: new Date().toISOString(),
              conversationId: selectedConversationId.value
            };
            // 确保最终消息被保存
            const existingMsgIndex = conversationMessages.value.findIndex(m => m.id === finalAiMessage.id);
            if (existingMsgIndex >= 0) {
              conversationMessages.value[existingMsgIndex] = finalAiMessage;
              await saveMessageToDB(finalAiMessage);
            } else if (!assistantMessageAdded) {
                // 如果流结束时还没添加过助手消息 (例如非流式或只有DONE)
                conversationMessages.value.push(finalAiMessage);
                await saveMessageToDB(finalAiMessage);
            } else {
                 // 如果助手消息已添加，确保最终内容被保存
                 const idx = conversationMessages.value.findIndex(m => m.id === aiMessageId);
                 if(idx >=0 ) await saveMessageToDB(conversationMessages.value[idx]);
            }
            
            // 更新对话时间
             const conv = conversations.value.find(c => c.id === selectedConversationId.value);
             if (conv) {
               conv.updated_at = new Date().toISOString();
               conv.updatedAt = new Date().toISOString();
               await saveConversationToDB(conv);
             }
          }
        }

      } catch (error) {
        console.error('处理多图片消息失败:', error);
        // 移除临时用户消息
        const tempIndex = conversationMessages.value.findIndex(m => m.id === tempUserMessageId);
        if (tempIndex >= 0) {
          conversationMessages.value.splice(tempIndex, 1);
        }
        // 显示错误消息
        conversationMessages.value.push({
          id: 'error_multi_' + Date.now(),
          role: 'system',
          content: `发送多图片消息失败: ${error.message}`,
          created_at: new Date().toISOString(),
          createdAt: new Date().toISOString(),
          conversationId: selectedConversationId.value,
          error: true
        });
      } finally {
        isConversationLoading.value = false;
      }
    };

    return {
      // 用户相关状态
      isLoggedIn,
      currentUser,
      userDialogVisible,
      userDialogMode,
      
      // 对话相关状态
      conversations,
      selectedConversationId,
      conversationMessages,
      isConversationLoading,
      isProcessing,
      
      // 模型相关状态
      availableModels,
      currentModel,
      supportedFileTypes,
      
      // 方法
      showUserDialog,
      handleAuthSuccess,
      handleLogout,
      handleSelectConversation,
      handleNewConversation,
      sendMessage,
      handleFileUpload,
      handleModelChange,
      messageListRef,
      currentModelCapabilities,
      currentModelName,
      currentModelType,
      deleteConversation,
      renameConversation,
      handleMultiFileUpload,
      handleSendMultiImages
    }
  }
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
  overflow: hidden;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
  z-index: 10;
  flex-shrink: 0;
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
  font-size: 18px;
  margin: 0;
  color: #333;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.main-container {
  flex: 1;
  padding: 24px;
  background-color: #f0f2f5;
  display: flex;
  gap: 24px;
  overflow: hidden;
  position: relative;
  height: calc(100vh - 70px); /* 减去header高度 */
}

.conversation-panel {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.chat-display {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
  min-width: 0;
  height: 100%;
}

.model-selector {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 2;
  background-color: #fff;
  padding: 4px 8px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-model {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  border-right: 1px solid #f0f0f0;
}

.model-name {
  font-weight: 500;
  color: #333;
  font-size: 13px;
}

.model-type {
  font-size: 11px;
  color: #909399;
  padding: 1px 4px;
  background-color: #f5f7fa;
  border-radius: 3px;
}

.model-select {
  width: 100px;
}

.model-select :deep(.el-input__wrapper) {
  padding: 0 8px;
}

.model-select :deep(.el-input__inner) {
  height: 28px;
  line-height: 28px;
  font-size: 13px;
}

.messages-area {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 120px;
  overflow-y: auto;
  padding: 20px;
  height: auto;
  z-index: 1;
}

/* 确保消息内容可以换行 */
.messages-area :deep(.message-content) {
  white-space: pre-wrap;
  word-wrap: break-word;
  max-width: 100%;
}

.input-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
  background-color: #fff;
  padding: 24px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: center;
  height: auto;
  min-height: 120px;
}

@media (max-width: 768px) {
  .main-container {
    padding: 16px;
    gap: 16px;
  }
  
  .conversation-panel {
    width: 260px;
  }
  
  .messages-area {
    bottom: 100px;
  }
  
  .input-container {
    padding: 16px;
    min-height: 100px;
  }

  .model-selector {
    top: 12px;
    right: 12px;
    padding: 3px 6px;
  }

  .current-model {
    display: none;
  }

  .model-select {
    width: 90px;
  }
}

@media (max-width: 576px) {
  .main-container {
    padding: 0;
    flex-direction: column;
    height: calc(100vh - 70px);
  }
  
  .conversation-panel {
    width: 100%;
    height: 40vh;
    border-radius: 0;
    flex-shrink: 0;
  }
  
  .chat-display {
    height: 60vh;
    border-radius: 0;
    flex: 1;
  }
  
  .messages-area {
    padding-bottom: 90px;
  }
  
  .input-container {
    bottom: 12px;
    padding: 0 12px;
  }
}
</style>

<style>
/* 移除全局样式，这些样式应该放在全局CSS文件中 */
</style>
