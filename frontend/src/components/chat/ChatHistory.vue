<template>
  <div class="chat-history">
    <!-- 顶部操作栏 -->
    <div class="history-header">
      <h2>对话历史</h2>
      <el-button type="primary" @click="$emit('new-conversation')">
        <el-icon><Plus /></el-icon>
        新对话
      </el-button>
    </div>
    
    <!-- 对话列表 -->
    <div class="history-list" ref="listRef">
      <el-scrollbar>
        <div
          v-for="conversation in conversations"
          :key="conversation.id"
          class="history-item"
          :class="{ active: conversation.id === activeConversationId }"
          @click="$emit('select-conversation', conversation.id)"
        >
          <div class="item-content">
            <el-icon class="item-icon"><ChatDotRound /></el-icon>
            <div class="item-info">
              <div class="item-title">{{ conversation.title || '新对话' }}</div>
              <div class="item-meta">
                <span class="item-time">{{ formatTime(conversation.updatedAt) }}</span>
                <span class="item-model">{{ getModelName(conversation.model) }}</span>
              </div>
            </div>
          </div>
          <div class="item-actions">
            <el-dropdown trigger="click" @command="handleCommand">
              <el-button link class="action-button">
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="rename">重命名</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        
        <!-- 空状态 -->
        <el-empty
          v-if="conversations.length === 0"
          description="暂无对话历史"
        >
          <el-button type="primary" @click="$emit('new-conversation')">
            开始新对话
          </el-button>
        </el-empty>
      </el-scrollbar>
    </div>
    
    <!-- 重命名对话框 -->
    <el-dialog
      v-model="renameDialogVisible"
      title="重命名对话"
      width="400px"
    >
      <el-form :model="renameForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="renameForm.title" placeholder="请输入对话标题" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="renameDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleRename">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ChatDotRound, Plus, More } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default {
  name: 'ChatHistory',
  components: {
    ChatDotRound,
    Plus,
    More
  },
  props: {
    conversations: {
      type: Array,
      required: true
    },
    activeConversationId: {
      type: [String, Number],
      default: null
    }
  },
  emits: ['select-conversation', 'new-conversation', 'rename-conversation', 'delete-conversation'],
  setup(props, { emit }) {
    const listRef = ref(null)
    const renameDialogVisible = ref(false)
    const renameForm = ref({
      id: null,
      title: ''
    })
    
    // 格式化时间
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      return formatDistanceToNow(new Date(timestamp), {
        addSuffix: true,
        locale: zhCN
      })
    }
    
    // 获取模型名称
    const getModelName = (modelId) => {
      const modelMap = {
        'qwen-turbo': '通义千问-Turbo',
        'qwen-plus': '通义千问-Plus',
        'qwen-max-latest': '通义千问-Max',
        'qwen-omni-turbo': '通义千问-Omni'
      }
      return modelMap[modelId] || modelId
    }
    
    // 处理下拉菜单命令
    const handleCommand = (command) => {
      if (command === 'rename') {
        const conversation = props.conversations.find(c => c.id === props.activeConversationId)
        if (conversation) {
          renameForm.value = {
            id: conversation.id,
            title: conversation.title || ''
          }
          renameDialogVisible.value = true
        }
      } else if (command === 'delete') {
        ElMessageBox.confirm(
          '确定要删除这个对话吗？此操作不可恢复。',
          '删除对话',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(() => {
          emit('delete-conversation', props.activeConversationId)
        }).catch(() => {
          // 用户取消删除
        })
      }
    }
    
    // 处理重命名
    const handleRename = () => {
      if (!renameForm.value.title.trim()) {
        ElMessage.warning('请输入对话标题')
        return
      }
      
      emit('rename-conversation', {
        id: renameForm.value.id,
        title: renameForm.value.title.trim()
      })
      
      renameDialogVisible.value = false
    }
    
    return {
      listRef,
      renameDialogVisible,
      renameForm,
      formatTime,
      getModelName,
      handleCommand,
      handleRename
    }
  }
}
</script>

<style scoped>
.chat-history {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.history-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #f8f9fa;
}

.history-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.history-list {
  flex: 1;
  overflow: hidden;
  padding: 16px;
}

.history-item {
  padding: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.history-item:hover {
  background-color: #f3f4f6;
  border-color: #e4e7ed;
}

.history-item.active {
  background-color: #e6f3ff;
  border-color: #409eff;
}

.item-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.item-icon {
  font-size: 20px;
  color: #409eff;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  color: #1f2937;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
}

.item-time {
  white-space: nowrap;
}

.item-model {
  padding: 2px 6px;
  background-color: #f3f4f6;
  border-radius: 4px;
  font-size: 11px;
}

.item-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.history-item:hover .item-actions {
  opacity: 1;
}

.action-button {
  padding: 4px;
  color: #6b7280;
}

.action-button:hover {
  color: #409eff;
}

@media (max-width: 768px) {
  .history-header {
    padding: 16px;
  }
  
  .history-list {
    padding: 12px;
  }
  
  .history-item {
    padding: 12px;
  }
  
  .item-title {
    font-size: 13px;
  }
  
  .item-meta {
    font-size: 11px;
  }
}
</style>
