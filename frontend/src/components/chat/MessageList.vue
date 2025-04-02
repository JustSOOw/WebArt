<template>
  <div class="message-list" ref="listRef">
    <el-scrollbar ref="scrollbarRef" @scroll="handleScroll" class="messages-scrollbar">
      <div class="message-container">
        <!-- 加载更多按钮 -->
        <div v-if="hasMore" class="load-more">
          <el-button 
            type="primary" 
            link 
            :loading="loading"
            @click="loadMore"
          >
            加载更多消息
          </el-button>
        </div>
        
        <!-- 消息列表 -->
        <div
          v-for="message in messages"
          :key="message.id"
          class="message-item"
          :class="{
            'message-user': message.role === 'user',
            'message-assistant': message.role === 'assistant',
            'message-system': message.role === 'system',
            'message-error': message.error || message.isError
          }"
        >
          <!-- 头像 -->
          <div class="message-avatar">
            <el-avatar :size="40">
              <el-icon v-if="message.role === 'user'"><User /></el-icon>
              <el-icon v-else-if="message.role === 'assistant'"><ChatSquare /></el-icon>
              <el-icon v-else><Warning /></el-icon>
            </el-avatar>
          </div>
          
          <!-- 消息内容 -->
          <div class="message-content">
            <!-- 消息头部 -->
            <div class="message-header">
              <span class="message-role">
                {{ getRoleName(message.role) }}
              </span>
              <span class="message-time">
                {{ formatTime(message.createdAt || message.created_at) }}
              </span>
            </div>
            
            <!-- 消息主体 -->
            <div class="message-body">
              <template v-if="message.role === 'system' || message.error || message.isError">
                <div class="system-message">
                  {{ message.content }}
                </div>
              </template>
              <template v-else>
                <!-- 优先显示 Base64 媒体 -->
                <div v-if="message.media_base64" class="media-preview">
                  <el-image 
                    v-if="message.media_type === 'image'"
                    :src="message.media_base64"
                    :preview-src-list="[message.media_base64]"
                    fit="cover"
                    class="preview-image"
                  />
                  <!-- 可以为 audio 和 video 添加相应的预览组件 -->
                  <div v-else-if="message.media_type === 'audio'" class="audio-preview">
                    <audio controls :src="message.media_base64"></audio>
                  </div>
                  <div v-else-if="message.media_type === 'video'" class="video-preview">
                    <video controls width="250" :src="message.media_base64"></video>
                  </div>
                </div>
                <!-- 其次显示 URL 媒体 -->
                <div v-else-if="message.media_url" class="media-preview">
                  <el-image 
                    v-if="message.media_type === 'image'"
                    :src="getAbsoluteUrl(message.media_url)"
                    :preview-src-list="[getAbsoluteUrl(message.media_url)]"
                    fit="cover"
                    class="preview-image"
                  />
                  <!-- 可以为 audio 和 video 添加相应的预览组件 -->
                   <div v-else-if="message.media_type === 'audio'" class="audio-preview">
                    <audio controls :src="getAbsoluteUrl(message.media_url)"></audio>
                  </div>
                  <div v-else-if="message.media_type === 'video'" class="video-preview">
                    <video controls width="250" :src="getAbsoluteUrl(message.media_url)"></video>
                  </div>
                   <div v-else-if="message.media_type === 'document'" class="document-link">
                    <a :href="getAbsoluteUrl(message.media_url)" target="_blank" rel="noopener noreferrer">
                      <el-icon><Document /></el-icon>
                      {{ message.media_url.split('/').pop() }} <!-- 显示文件名 -->
                    </a>
                  </div>
                </div>
                
                <!-- 新增：处理多图片消息 -->
                <div v-else-if="message.media_type === 'image_multi' && message.files_info" class="multi-image-info">
                  <div class="multi-image-header">发送了 {{ message.files_info.length }} 张图片:</div>
                  <ul class="file-list">
                    <li v-for="(file, index) in message.files_info" :key="index">
                      <el-icon><Picture /></el-icon>
                      <span>{{ file.name }}</span> 
                      <span class="file-size">({{ (file.size / 1024).toFixed(1) }} KB)</span>
                    </li>
                  </ul>
                  <!-- 注意：这里不显示图片预览，因为Base64未存储 -->
                </div>
                
                <!-- 渲染文本内容 (如果存在或为占位符) -->
                <div v-if="message.content && message.content.trim() !== ''" class="text-content" v-html="formatContent(message.content)"></div>
                
                <!-- 从文本中提取的 Markdown 图片 (作为补充) -->
                <div v-if="hasImages(message.content)" class="image-preview">
                  <el-image
                    v-for="(url, index) in extractImages(message.content)"
                    :key="index"
                    :src="url"
                    :preview-src-list="extractImages(message.content)"
                    fit="cover"
                    class="preview-image"
                  />
                </div>
              </template>
            </div>
            
            <!-- 消息操作 -->
            <div class="message-actions">
              <el-button 
                v-if="message.role === 'assistant'"
                link
                size="small"
                @click="copyMessage(message.content)"
              >
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
            </div>
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-messages">
          <el-skeleton :rows="3" animated />
        </div>
        
        <!-- 空状态 -->
        <el-empty
          v-if="!loading && messages.length === 0"
          description="暂无消息"
        >
          <template #image>
            <el-icon class="empty-icon"><ChatDotRound /></el-icon>
          </template>
        </el-empty>
      </div>
    </el-scrollbar>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, watch } from 'vue'
import { User, ChatSquare, Warning, ChatDotRound, CopyDocument, Document, Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import DOMPurify from 'dompurify'
import { marked } from 'marked'

export default {
  name: 'MessageList',
  components: {
    User,
    ChatSquare,
    Warning,
    ChatDotRound,
    CopyDocument,
    Document,
    Picture
  },
  props: {
    messages: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    hasMore: {
      type: Boolean,
      default: false
    }
  },
  emits: ['load-more'],
  setup(props, { emit }) {
    const listRef = ref(null)
    const scrollbarRef = ref(null)
    
    // 获取角色名称
    const getRoleName = (role) => {
      const roleMap = {
        user: '我',
        assistant: 'AI助手',
        system: '系统'
      }
      return roleMap[role] || role
    }
    
    // 格式化时间
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      return formatDistanceToNow(new Date(timestamp), {
        addSuffix: true,
        locale: zhCN
      })
    }
    
    // 格式化消息内容（支持Markdown）
    const formatContent = (content) => {
      if (!content) return ''
      
      // 使用marked解析Markdown
      const html = marked(content)
      
      // 使用DOMPurify清理HTML
      return DOMPurify.sanitize(html, {
        ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'code', 'pre', 'a', 'ul', 'ol', 'li', 'blockquote'],
        ALLOWED_ATTR: ['href', 'target']
      })
    }
    
    // 检查消息是否包含图片
    const hasImages = (content) => {
      if (!content) return false
      return /!\[.*?\]\((.*?)\)/g.test(content)
    }
    
    // 提取消息中的图片URL
    const extractImages = (content) => {
      if (!content) return []
      const matches = content.matchAll(/!\[.*?\]\((.*?)\)/g)
      return Array.from(matches).map(match => match[1])
    }
    
    // 复制消息内容
    const copyMessage = async (content) => {
      try {
        await navigator.clipboard.writeText(content)
        ElMessage.success('已复制到剪贴板')
      } catch (error) {
        console.error('复制失败:', error)
        ElMessage.error('复制失败')
      }
    }
    
    // 加载更多消息
    const loadMore = () => {
      emit('load-more')
    }
    
    // 处理滚动
    const handleScroll = (e) => {
      const { scrollTop } = e.target
      
      // 如果滚动到顶部，触发加载更多
      if (scrollTop === 0 && props.hasMore && !props.loading) {
        loadMore()
      }
    }
    
    // 添加获取绝对路径的方法，处理相对URL
    const getAbsoluteUrl = (url) => {
      if (!url) return ''
      if (url.startsWith('http') || url.startsWith('data:')) {
        return url
      }
      // 假设相对路径是相对于服务器根目录的
      return `${window.location.origin}${url}`
    }
    
    // 滚动到底部
    const scrollToBottom = () => {
      // 使用 setTimeout 给予浏览器更多渲染时间 (或让 el-scrollbar 内部准备好)
      setTimeout(() => {
        // 尝试使用 el-scrollbar 的 scrollTo 方法
        if (scrollbarRef.value && typeof scrollbarRef.value.scrollTo === 'function') {
            // 仍然需要 wrap 来获取 scrollHeight
            // 根据 Element Plus 版本，可能是 wrapRef 或 wrap
            const scrollContainer = scrollbarRef.value.wrapRef || scrollbarRef.value.wrap;
            
            if (scrollContainer) {
                const scrollHeight = scrollContainer.scrollHeight;
                const clientHeight = scrollContainer.clientHeight;
                  
                if (scrollHeight > clientHeight) {
                    scrollbarRef.value.scrollTo({ top: scrollHeight, behavior: 'auto' }); // 使用 auto 避免平滑滚动可能带来的问题
                    
                    // 短暂延迟后检查 scrollTop 是否接近 scrollHeight
                    setTimeout(() => {
                        if (scrollContainer) { // 再次检查，以防万一
                           const currentScrollTop = scrollContainer.scrollTop;
                        } else {
                           // console.warn('[MessageList Debug] scrollContainer became unavailable in inner setTimeout.'); // 保留注释以备将来调试
                        }
                    }, 50); // 稍长延迟检查
                } else {
                }
            } else {
                console.warn('[MessageList] Scroll container (wrap or wrapRef) not found on scrollbarRef.'); // 保留这个警告，因为它可能表示配置问题
            }
            
        } else {
          console.warn('[MessageList] scrollbarRef.value missing or scrollTo method not available.'); // 保留这个警告
        }
      }, 50); // 调回延迟到 50ms，因为组件方法可能更可靠
    }
    
    // 监听消息列表变化，自动滚动到底部
    watch(() => props.messages, (newMessages, oldMessages) => {
      // 可以在这里也稍微延迟，避免过于频繁的滚动尝试
      // 但通常在 scrollToBottom 内部延迟就够了
      scrollToBottom()
    }, { deep: true, flush: 'post' }) // 使用 flush: 'post' 确保在组件更新后触发 watch
    
    // 初始化时滚动到底部
    onMounted(() => {
      scrollToBottom()
    })
    
    return {
      listRef,
      scrollbarRef,
      getRoleName,
      formatTime,
      formatContent,
      hasImages,
      extractImages,
      copyMessage,
      loadMore,
      handleScroll,
      getAbsoluteUrl
    }
  }
}
</script>

<style scoped>
.message-list {
  flex: 1;
  width: 100%;
  height: 100%;
  background-color: #f8f9fa;
  position: relative;
}

.messages-scrollbar {
  height: 100%;
  overflow: hidden;
}

.message-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.load-more {
  text-align: center;
  padding: 16px 0;
}

.message-item {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  animation: fadeIn 0.3s ease;
  max-width: 100%;
}

.message-item.message-user {
  flex-direction: row-reverse;
}

.message-item:last-child {
  margin-bottom: 0;
}

.message-avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 2px solid #fff;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  flex: 1;
  min-width: 0;
  max-width: 80%;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding: 0 4px;
}

.message-user .message-header {
  flex-direction: row-reverse;
}

.message-role {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.message-time {
  font-size: 12px;
  color: #6b7280;
}

.message-body {
  background-color: #fff;
  border-radius: 16px;
  padding: 16px;
  line-height: 1.6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e4e7ed;
  position: relative;
}

.message-user .message-body {
  background-color: #e6f3ff;
  margin-left: 0;
  margin-right: 40px;
  border-color: #409eff;
}

.message-assistant .message-body {
  background-color: #fff;
  margin-left: 40px;
  margin-right: 0;
  border-color: #e4e7ed;
}

.message-system .message-body {
  background-color: #fff3e0;
  margin: 0 auto;
  max-width: 80%;
  border-color: #ff9800;
}

.message-error .message-body {
  background-color: #ffebee;
  margin: 0 auto;
  max-width: 80%;
  border-color: #f44336;
}

.system-message {
  color: var(--warning-color);
  font-size: 14px;
}

.text-content {
  color: #1f2937;
  font-size: 14px;
}

.text-content :deep(p) {
  margin: 0 0 12px;
}

.text-content :deep(code) {
  background-color: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  color: #1f2937;
}

.text-content :deep(pre) {
  background-color: #f3f4f6;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
  border: 1px solid #e4e7ed;
}

.text-content :deep(blockquote) {
  margin: 12px 0;
  padding: 12px 16px;
  border-left: 4px solid #409eff;
  background-color: #f3f4f6;
  border-radius: 0 8px 8px 0;
  color: #1f2937;
}

.image-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.preview-image {
  width: 100%;
  height: 200px;
  border-radius: 8px;
  cursor: pointer;
  object-fit: cover;
  transition: transform 0.2s;
  border: 1px solid #e4e7ed;
}

.preview-image:hover {
  transform: scale(1.02);
}

.message-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  padding: 0 4px;
}

.message-user .message-actions {
  flex-direction: row-reverse;
}

.loading-messages {
  padding: 20px;
}

.empty-icon {
  font-size: 48px;
  color: #6b7280;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .message-container {
    padding: 16px;
  }
  
  .message-item {
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .message-body {
    padding: 12px;
  }
  
  .message-user .message-body {
    margin-right: 20px;
  }
  
  .message-assistant .message-body {
    margin-left: 20px;
  }
  
  .image-preview {
    grid-template-columns: 1fr;
  }
  
  .preview-image {
    height: 180px;
  }
}

@media (max-width: 576px) {
  .message-container {
    padding: 12px;
  }
}

.media-preview,
.multi-image-info { /* 应用到新的多图片信息块 */
  margin-bottom: 8px;
}

.preview-image {
  max-width: 200px;
  max-height: 200px;
  border-radius: 6px;
  cursor: pointer;
}

.audio-preview audio,
.video-preview video {
  max-width: 100%;
  border-radius: 6px;
}

.document-link a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--el-color-primary);
  text-decoration: none;
}

.document-link a:hover {
  text-decoration: underline;
}

/* 新增：多图片信息样式 */
.multi-image-info {
  background-color: #f7f7f7;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
}

.multi-image-header {
  font-weight: 500;
  margin-bottom: 6px;
  color: #606266;
}

.file-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.file-list li {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
  color: #909399;
}

.file-list .el-icon {
  font-size: 16px;
}

.file-size {
  margin-left: 4px;
  font-size: 12px;
}

.text-content {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.text-content :deep(p) {
  margin: 0 0 8px 0;
}

.text-content :deep(pre) {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.text-content :deep(code) {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9em;
}

.message-actions {
  margin-top: 8px;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.message-item:hover .message-actions {
  opacity: 1;
}
</style>
