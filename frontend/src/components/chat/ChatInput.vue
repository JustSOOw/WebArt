<template>
  <div class="chat-input">
    <div class="card-container" :class="{'has-file': selectedFiles.length > 0}">
      <!-- 文本输入区域 (包含显示和实际输入) -->
      <div class="input-area-wrapper">
          <!-- 卡片显示区域 (仅用于显示文件和文本) -->
          <div class="card-content" @click="focusInput"> 
              <!-- 文件信息 -->
              <div class="file-info-container" v-if="selectedFiles && selectedFiles.length > 0">
                  <div class="file-info" :class="{'multiple': selectedFiles.length > 1}">
                      <el-icon><Document /></el-icon>
                      <span class="file-name" :title="getFilesInfo()">
                          {{ getShortFileName(selectedFiles[0].name) }}
                          <span v-if="selectedFiles.length > 1">+{{ selectedFiles.length - 1 }}个文件</span>
                      </span>
                      <el-button link @click.stop="clearFiles" class="delete-btn"> 
                          <el-icon><Delete /></el-icon>
                      </el-button>
                  </div>
              </div>
              
              <!-- 直接在这里放置输入框，不使用覆盖层 -->
              <div class="input-container">
                  <div class="placeholder" v-if="!inputContent && !inputFocused">问问题，尽管问...</div>
                  <el-input
                      v-model="inputContent"
                      type="textarea"
                      :rows="1"
                      :maxlength="2000"
                      :disabled="loading"
                      ref="inputRef"
                      @input="updateHeightAndScroll"
                      @keydown.enter.prevent="handleKeydown"
                      @focus="handleFocus"
                      @blur="handleBlur"
                      resize="none"
                      class="transparent-textarea"
                  />
              </div>
          </div>
      </div>
      
      <!-- 按钮区域 -->
      <div class="card-actions">
        <el-upload
          v-if="showUpload"
          class="upload-button"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleFileChange"
          :before-upload="beforeUpload"
          :multiple="true"
          ref="uploadRef"
        >
          <el-icon><Upload /></el-icon>
        </el-upload>
        
        <div class="send-button" :class="{ 'can-send': canSend }" @click="handleSend">
          <el-icon><Position /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick, onMounted } from 'vue'
import { Upload, Position, Document, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'ChatInput',
  components: {
    Upload,
    Position,
    Document,
    Delete
  },
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    supportedFileTypes: {
      type: Array,
      default: () => []
    },
    showUpload: {
      type: Boolean,
      default: true
    },
    modelId: {
      type: String,
      default: ''
    }
  },
  emits: ['send-message', 'upload-file', 'upload-files', 'send-multi-images'],
  setup(props, { emit }) {
    const inputContent = ref('')
    const selectedFile = ref(null)
    const selectedFiles = ref([])
    const inputRef = ref(null)
    const uploadRef = ref(null)  // 添加 el-upload 组件的引用
    const inputFocused = ref(false)
    
    // 计算是否可以发送消息
    const canSend = computed(() => {
      // 必须有文本内容才能发送，即使选择了文件
      return inputContent.value.trim() !== ''
    })
    
    // 聚焦输入框
    const focusInput = () => {
      if (inputRef.value) {
        inputRef.value.focus()
        inputFocused.value = true
      }
    }
    
    
    // 处理输入框失焦
    const handleBlur = () => {
      // 如果输入框有内容，保持聚焦状态
      // 否则恢复未聚焦状态
      if (!inputContent.value.trim()) {
        inputFocused.value = false
      }
    }
    
    // 处理输入框聚焦
    const handleFocus = () => {
        inputFocused.value = true;
    };
    
    // 更新输入框高度，并同步滚动条
    const updateHeightAndScroll = () => {
      nextTick(() => {
        if (inputRef.value) {
            const textarea = inputRef.value.$el.querySelector('textarea');
            if (textarea) {
                // 保存当前滚动位置
                const scrollTop = textarea.scrollTop;
                
                // 自动调整高度
                textarea.style.height = '32px'; // 先设置一个最小高度，考虑内边距
                // 使用更大的最大高度，使输入框能适度增长
                const newHeight = Math.min(textarea.scrollHeight, 180); // 最大180px，与CSS中保持一致
                // 设置新的高度，确保内容完全显示
                textarea.style.height = (newHeight < 32 ? 32 : newHeight) + 'px';
                
                // 如果达到最大高度，恢复滚动位置，确保滚动条位置正确
                if (newHeight >= 180) {
                    setTimeout(() => {
                        textarea.scrollTop = scrollTop;
                    }, 0);
                }
            }
        }
      });
    };
    
    // 主要用来更新文件列表，现在包含所有验证逻辑
    const handleFileChange = async (uploadFile, uploadFiles) => {
      // el-upload 的 onChange 会在文件状态改变时触发多次
      // 我们只关心 status === 'ready' 的初始状态
      if (uploadFile.status !== 'ready') {
          return;
      }
      
      // ==== 针对多文件同时选择的情况 ====
      // 找出当前批次同时选择的所有文件（status为'ready'的文件）
      const currentBatchFiles = uploadFiles.filter(f => f.status === 'ready');
      
      // 如果是多文件批次，需要先验证所有文件类型是否一致
      if (currentBatchFiles.length > 1) {
        // 第一个文件的扩展名
        const firstFileExt = '.' + currentBatchFiles[0].raw.name.split('.').pop().toLowerCase();
        const isFirstImage = ['.jpg', '.jpeg', '.png', '.gif'].includes(firstFileExt);
        
        // 如果第一个不是图片，批量选择就不允许
        if (!isFirstImage) {
          ElMessage.error(`批量选择仅支持图片文件，请单独选择其他类型的文件`);
          
          // 移除所有当前批次的文件
          currentBatchFiles.forEach(f => {
            const idx = uploadFiles.findIndex(uf => uf.uid === f.uid);
            if (idx !== -1) uploadFiles.splice(idx, 1);
          });

          return;
        }
        
        // 验证所有文件是否都是图片
        for (const f of currentBatchFiles) {
          const ext = '.' + f.raw.name.split('.').pop().toLowerCase();
          if (!['.jpg', '.jpeg', '.png', '.gif'].includes(ext)) {
            ElMessage.error(`批量选择仅支持图片文件，检测到非图片文件: ${f.raw.name}`);
            
            // 移除所有当前批次的文件
            currentBatchFiles.forEach(f => {
              const idx = uploadFiles.findIndex(uf => uf.uid === f.uid);
              if (idx !== -1) uploadFiles.splice(idx, 1);
            });

            return;
          }
        }
        
        // 计算批次的总大小
        let batchTotalSize = currentBatchFiles.reduce((sum, f) => sum + f.raw.size, 0);
        
        // 计算已有文件总大小
        let existingSize = selectedFiles.value.reduce((sum, f) => sum + f.size, 0);
        // 批次加上已有文件的总大小
        let newTotalSize = existingSize + batchTotalSize;
        
        
        // 验证总大小是否会超过限制 (批次本身 + 已选)
        const MAX_TOTAL_SIZE = 15 * 1024 * 1024; // 多图片总大小限制15MB
        if (newTotalSize > MAX_TOTAL_SIZE) {
          ElMessage.error(`多图片上传总大小超过限制 (最大 ${(MAX_TOTAL_SIZE / 1024 / 1024).toFixed(0)}MB，Base64后约 ${(MAX_TOTAL_SIZE / 1024 / 1024 * 1.33).toFixed(0)}MB)`);
          
          // 移除所有当前批次的文件
          currentBatchFiles.forEach(f => {
            const idx = uploadFiles.findIndex(uf => uf.uid === f.uid);
            if (idx !== -1) uploadFiles.splice(idx, 1);
          });
          
          return;
        }
      }
      
      // 获取当前批次是否已通过批量验证
      const batchValidated = currentBatchFiles.length > 1;
      
      const file = uploadFile.raw; // 获取原始 File 对象
      
      try {
        // --- 执行所有验证 --- 
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        // 使用let而不是const，以便后续可能的调整
        let isImage = ['.jpg', '.jpeg', '.png', '.gif'].includes(fileExtension);
        let isAudio = ['.mp3', '.wav', '.m4a'].includes(fileExtension);
        let isVideo = ['.mp4', '.mov', '.avi'].includes(fileExtension);
        
        // 更精确的文件类型判断
        const mimeType = file.type.toLowerCase();
        const isMimeImage = mimeType.startsWith('image/');
        const isMimeAudio = mimeType.startsWith('audio/');
        const isMimeVideo = mimeType.startsWith('video/');
        
        // 如果MIME类型和扩展名不匹配，可能是用户手动改了扩展名
        if ((isImage && !isMimeImage) || (isAudio && !isMimeAudio) || (isVideo && !isMimeVideo)) {
            // 这里可以选择失败或者使用MIME类型判断
            // 我们选择以MIME类型为准
            if (isMimeImage) {
                isImage = true;
                isAudio = false;
                isVideo = false;
            } else if (isMimeAudio) {
                isImage = false;
                isAudio = true;
                isVideo = false;
            } else if (isMimeVideo) {
                isImage = false;
                isAudio = false;
                isVideo = true;
            }
        }

        // 3. 设置基于文件类型的大小限制（考虑到base64编码增加约33%的大小）
        const MAX_IMAGE_SIZE = 7.5 * 1024 * 1024; // 图片最大7.5MB (base64后约10MB)
        const MAX_AUDIO_SIZE = 7.5 * 1024 * 1024; // 音频最大7.5MB (base64后约10MB)
        const MAX_VIDEO_SIZE = 15 * 1024 * 1024;  // 视频最大15MB (base64后约20MB)
        const MAX_DOC_SIZE = 7.5 * 1024 * 1024;   // 文档最大7.5MB (base64后约10MB)
        
        // 根据文件类型获取大小限制
        const getFileSizeLimit = (fileExt, fileType) => {
            if (isImage) return MAX_IMAGE_SIZE;
            if (isAudio) return MAX_AUDIO_SIZE;
            if (isVideo) return MAX_VIDEO_SIZE;
            return MAX_DOC_SIZE; // 默认文档大小
        };
        
        // 获取该文件类型的限制大小，并计算可读的MB值
        const fileSizeLimit = getFileSizeLimit(fileExtension, file.type);
        const fileSizeLimitMB = (fileSizeLimit / 1024 / 1024).toFixed(1);
        
        // 单文件大小验证 - 使用文件类型对应的大小限制
        // 即使通过了批量验证，也要对每个文件的大小进行验证
        if (file.size > fileSizeLimit) {
            let typeName = isImage ? "图片" : isAudio ? "音频" : isVideo ? "视频" : "文档";
            throw new Error(`${typeName}文件 ${file.name} 大小超过限制 (最大 ${fileSizeLimitMB}MB，Base64后约 ${(fileSizeLimitMB * 1.33).toFixed(1)}MB)`);
        }
        
        // 如果是图片且不是批量验证通过的，则需要检查总大小
        if (isImage && selectedFiles.value.length > 0 && !batchValidated) {
            const MAX_TOTAL_SIZE = 15 * 1024 * 1024; // 多图片总大小限制15MB
            
            // 重新计算当前已选择的图片总大小（实际文件大小）
            let currentImageSize = 0;
            selectedFiles.value.forEach(f => {
                currentImageSize += f.size;
            });
            
            // 加上新选择的图片大小
            let newTotalSize = currentImageSize + file.size;
            
            if (newTotalSize > MAX_TOTAL_SIZE) {
                throw new Error(`多图片上传总大小超过限制 (最大 ${(MAX_TOTAL_SIZE / 1024 / 1024).toFixed(0)}MB，Base64后约 ${(MAX_TOTAL_SIZE / 1024 / 1024 * 1.33).toFixed(0)}MB)`);
                
            }
        }
        
        // 考虑Base64编码后的大小增加（约33%）
        // 对于大型媒体文件进行额外检查，确保Base64后不会超过API限制
        if (isAudio || isVideo || (isImage && file.size > 4 * 1024 * 1024)) {
            // 估算Base64编码后的大小
            const estimatedBase64Size = Math.ceil(file.size * 1.33);
            const API_BASE64_LIMIT = 20 * 1024 * 1024; // 20MB API调用限制
            
            if (estimatedBase64Size > API_BASE64_LIMIT) {
                throw new Error(`文件Base64编码后将超过API限制 (最大 ${(API_BASE64_LIMIT / 1024 / 1024).toFixed(0)}MB)`);
            }
        }

        // 移除旧的文件类型验证（#4），因为我们使用supportedFileTypes来检查
        if (!props.supportedFileTypes.includes(fileExtension)) {
            throw new Error(`不支持的文件类型: ${fileExtension}`);
        }
        
        // 6. 详细媒体文件验证 (异步)
        if (isImage || isAudio || isVideo) {
            await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const dataUrl = e.target.result;
                    if (isImage) {
                        const img = new Image();
                        img.onload = () => {
                            if (img.naturalWidth <= 10 || img.naturalHeight <= 10) {
                                return reject(new Error(`图片 ${file.name} 尺寸过小 (需大于 10x10像素)`));
                            }
                            const aspectRatio = img.naturalWidth / img.naturalHeight;
                            if (aspectRatio > 200 || aspectRatio < 1/200) {
                                return reject(new Error(`图片 ${file.name} 宽高比超出限制 (1:200 到 200:1 之间)`));
                            }
                            resolve(true);
                        };
                        img.onerror = () => {
                            reject(new Error(`无法加载图片 ${file.name} 进行验证`));
                        };
                        img.src = dataUrl;
                    } else if (isAudio) {
                        const audio = document.createElement('audio');
                        const cleanupAudio = () => { try { document.body.removeChild(audio); } catch(e){} };
                        audio.onloadedmetadata = () => {
                            if (!isNaN(audio.duration) && isFinite(audio.duration) && audio.duration > 180) {
                                cleanupAudio();
                                return reject(new Error(`音频 ${file.name} 时长超过限制 (${audio.duration.toFixed(1)}s > 180s)`));
                            }
                            cleanupAudio();
                            resolve(true);
                        };
                        audio.onerror = (err) => {
                            cleanupAudio();
                            reject(new Error(`无法加载音频 ${file.name}. Error: ${err.message || err.type}`));
                        };
                        audio.preload = 'metadata';
                        audio.src = dataUrl;
                        audio.style.display = 'none';
                        document.body.appendChild(audio);
                        audio.addEventListener('error', cleanupAudio, { once: true });
                    } else if (isVideo) {
                        const video = document.createElement('video');
                        const cleanupVideo = () => { try { document.body.removeChild(video); } catch(e){} };
                        video.onloadedmetadata = () => {
                            if (!isNaN(video.duration) && isFinite(video.duration) && video.duration > 40) {
                                cleanupVideo();
                                return reject(new Error(`视频 ${file.name} 时长超过限制 (${video.duration.toFixed(1)}s > 40s)`));
                            }
                            cleanupVideo();
                            resolve(true);
                        };
                        video.onerror = (err) => {
                            cleanupVideo();
                            reject(new Error(`无法加载视频 ${file.name}. Error: ${err.message || err.type}`));
                        };
                        video.preload = 'metadata';
                        video.src = dataUrl;
                        video.style.display = 'none';
                        document.body.appendChild(video);
                        video.addEventListener('error', cleanupVideo, { once: true });
                    }
                };
                reader.onerror = () => {
                    reject(new Error(`无法读取文件 ${file.name} 进行验证`));
                };
                reader.readAsDataURL(file);
            });
        }
        
        // --- 所有异步操作完成后的最终检查点 --- 
        
        // 1. 最终数量检查
        if (selectedFiles.value.length >= 10) {
             throw new Error(`文件选择已达上限 (最多 10 个)`);
        }
        
        // 2. 最终混合规则检查
        if (selectedFiles.value.length >= 1 && !isImage) {
             throw new Error(`多文件选择仅支持图片文件`);
        }
        
        // 3. 最终总大小检查
        const currentSelectedSize = selectedFiles.value.reduce((sum, f) => sum + f.size, 0);
        const potentialTotalSize = currentSelectedSize + file.size;
        const MAX_TOTAL_SIZE_FINAL = 15 * 1024 * 1024; 
        if (potentialTotalSize > MAX_TOTAL_SIZE_FINAL) {
            throw new Error(`添加此文件将导致总大小超过限制 (最大 ${(MAX_TOTAL_SIZE_FINAL / 1024 / 1024).toFixed(0)}MB)`);
        }
        
        // 最终检查通过，且文件不重复，则添加
        if (!selectedFiles.value.some(f => f.uid === file.uid)) {
            selectedFiles.value.push(file);
        }
        
      } catch (error) {
          ElMessage.error(error.message);
          // 从 el-upload 内部列表中移除验证失败的文件
          const index = uploadFiles.findIndex(f => f.uid === uploadFile.uid);
          if (index !== -1) {
              uploadFiles.splice(index, 1);
          }
      } finally {
          selectedFile.value = selectedFiles.value[0] || null;
      }
    };
    
    // 必须的beforeUpload函数，防止文件自动上传
    const beforeUpload = (file) => {
      // el-upload 在这里返回 false 时不会自动上传文件，而是触发 on-change 事件
      // 我们在 handleFileChange 中进行所有验证
      return false; 
    };
    
    // 清除已选择的文件
    const clearFile = () => {
      selectedFile.value = null
      clearFiles() // 调用统一的清理函数
    }
    
    // 清除所有文件
    const clearFiles = () => {
      selectedFiles.value = []
      selectedFile.value = null
      // 清除 el-upload 组件的文件列表
      if (uploadRef.value) {
        uploadRef.value.clearFiles()
      }
    }
    
    // 获取文件信息描述
    const getFilesInfo = () => {
      if (!selectedFiles.value.length) return ''
      if (selectedFiles.value.length === 1) return selectedFiles.value[0].name
      return `${selectedFiles.value.length}个文件: ${selectedFiles.value.map(f => f.name).join(', ')}`
    }
    
    // 处理按键
    const handleKeydown = (e) => {
      if (e.shiftKey) {
        // Shift + Enter 换行
        const textarea = e.target
        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        inputContent.value = inputContent.value.substring(0, start) + '\n' + inputContent.value.substring(end)
        // 设置光标位置到换行后
        nextTick(() => {
          textarea.selectionStart = textarea.selectionEnd = start + 1
        })
      } else {
        // Enter 发送
        handleSend()
      }
    }
    
    // 处理发送
    const handleSend = () => {
      if (!canSend.value || props.loading) {
        return;
      }
      
      // 获取当前输入框的文本内容
      const content = inputContent.value.trim();
      
      // 根据文件数量决定发送事件
      if (selectedFiles.value.length > 1) {
        // 确保所有文件都是图片 (虽然 beforeUpload 应该保证了)
        const allImages = selectedFiles.value.every(f => 
            ['.jpg', '.jpeg', '.png', '.gif'].includes('.' + f.name.split('.').pop().toLowerCase())
        );
        if (allImages) {
            emit('send-multi-images', { files: selectedFiles.value, message: content });
        } else {
            // 这理论上不应该发生，如果发生了说明 beforeUpload 逻辑有误
            ElMessage.error("多文件上传目前仅支持图片。");
            return; // 阻止发送
        }
      } else if (selectedFiles.value.length === 1) {
          // 单文件上传事件（可以是任何支持的类型）
          emit('upload-file', { file: selectedFiles.value[0], message: content });
      } else {
        // 纯文本消息
        emit('send-message', content);
      }
      
      // 清空输入和文件
      inputContent.value = '';
      clearFiles();

      // 强制更新高度
      nextTick(updateHeightAndScroll);


      
      // 显式重新聚焦输入框，确保 placeholder 不会错误显示
      nextTick(() => {
        inputRef.value?.focus();
      });
    };
    
    // 获取截断的文件名
    const getShortFileName = (name) => {
      if (!name) return ''
      const maxLength = 20
      if (name.length <= maxLength) return name
      return name.substring(0, maxLength - 3) + '...'
    }
    
    // 组件挂载后自动聚焦
    onMounted(() => {
      // 初始化时调整高度和文件信息高度
      updateHeightAndScroll()
    })
    
    return {
      inputContent,
      selectedFile,
      selectedFiles,
      inputRef,
      uploadRef,
      inputFocused,
      canSend,
      focusInput,
      handleBlur,
      updateHeightAndScroll,
      handleFileChange,
      clearFile,
      clearFiles,
      getFilesInfo,
      handleKeydown,
      handleSend,
      getShortFileName,
      Upload,
      Position,
      Document,
      Delete,
      handleFocus,
      beforeUpload
    };
  }
};
</script>

<style scoped>
.chat-input {
  width: 90%;
  max-width: 640px;
}

.card-container {
  background-color: #fff;
  border-radius: 18px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  padding: 0; /* 内边距由内部元素控制 */
  position: relative;
  min-height: 56px; /* 最小高度 */
  transition: all 0.3s ease;
  display: flex; /* 使用 flex 布局 */
  align-items: flex-end; /* 底部对齐 */
  max-height: 220px; /* 减小卡片最大高度 */
  overflow: hidden; /* 防止内容溢出 */
}


.card-container:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.hidden-input {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  opacity: 0;
}

.input-area-wrapper {
    flex: 1; /* 占据主要空间 */
    position: relative; /* 用于内部绝对定位 */
    /* padding: 8px 12px; */ /* 移除这里的 padding，让 overlay 控制 */
    min-height: 40px; /* 确保最小高度 */
    display: flex; /* 内部也用flex */
    flex-direction: column; /* 堆叠 card-content 和 real-input-overlay */
}

.card-content {
  /* 这个现在只负责背景显示和文件信息 */
  /* flex: 1; */
  padding: 12px 0 0 0; /* 只保留顶部内边距 */
  cursor: text;
  line-height: 1.5;
  display: flex;
  flex-direction: column;
  position: relative; /* 确保 z-index 生效 */
  z-index: 1; /* 在输入框下方 */
  flex-grow: 1; /* 允许内容区域增长 */
  max-height: 220px; /* 减小内容区域最大高度 */
  overflow: hidden; /* 确保内容不会溢出 */
}

/* 文件信息容器 */
.file-info-container {
    margin: 0 12px 16px 12px; /* 左右添加内边距，增加与输入区的间距 */
    width: 50%;
    z-index: 2; 
    position: relative;
    flex-shrink: 0; /* 防止被压缩 */
}

/* 文件信息 */
.file-info {
  background-color: #e9f5ff;
  border-radius: 8px;
  padding: 6px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #409eff;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.file-info.multiple {
  background-color: #f0f9eb;
  color: #67c23a;
}

.delete-btn {
  margin-left: auto;
  color: inherit;
  font-size: 16px;
  padding: 0;
  min-height: auto;
}

.delete-btn:hover {
  color: #f56c6c;
}

/* 添加新的输入容器样式 */
.input-container {
    flex-grow: 1;
    position: relative; /* 用于占位符定位 */
    padding: 0 12px 8px 12px; /* 统一的内边距 */
    min-height: 32px; /* 增加最小高度，适应新的文本区域高度 */
    max-height: 180px; /* 减小最大高度 */
    overflow: hidden; /* 不设置滚动，让内部的 textarea 负责滚动 */
}

.input-container.has-file {
    margin-top: 8px; /* 有文件时与文件信息之间增加间距 */
}

.placeholder {
  color: #a8abb2;
  position: absolute;
  top: 30%; /* 放置在容器的中部 */
  left: 10px;
  width: 100%;
  transform: translateY(-50%); /* 向上移动自身高度的一半 */
  line-height: 1.5; /* 保持和输入文本一致 */
  pointer-events: none;
  z-index: 1;
  display: block;
  padding-top: 0; 
}

/* 透明化 textarea */
.transparent-textarea :deep(textarea) {
    background-color: transparent !important;
    color: #303133 !important; 
    border: none !important;
    padding: 4px 0 !important; /* 添加上下内边距使光标居中 */
    margin: 0 !important;
    box-shadow: none !important;
    line-height: 1.5; /* 这个是多行文本的行高 */
    /* 将高度控制改为使用updateHeightAndScroll函数中动态设置 */
    min-height: 32px; /* 增加最小高度，与容器保持一致 */
    width: 100%; /* 确保宽度正确 */
    overflow-y: auto; /* 明确允许垂直滚动 */
    max-height: 180px; /* 减小最大高度限制 */
    z-index: 3; 
    position: relative; 
    display: block; /* 确保是块级元素 */
    pointer-events: auto; /* 确保可以点击和滚动 */
}

.card-actions {
  /* position: absolute; */ /* 不再绝对定位 */
  /* right: 16px; */
  /* bottom: 12px; */
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 8px; /* 与输入区分隔 */
  padding: 0 12px 8px 0; /* 调整 padding */
  align-self: flex-end; /* 确保按钮在底部 */
}

.upload-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: transparent;
  color: #888;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-button:hover {
  background-color: #f3f4f6;
  color: #409eff;
}

.send-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #eee;
  color: #bbb;
  cursor: not-allowed;
  transition: all 0.2s ease;
}

.send-button.can-send {
  background-color: #409eff;
  color: white;
  cursor: pointer;
}

.send-button.can-send:hover {
  background-color: #66b1ff;
}

@media (max-width: 768px) {
  .chat-input {
    width: 95%;
  }

  .card-container {
    padding: 12px;
  }

  .card-actions {
    right: 12px;
    bottom: 10px;
  }
  
  .file-info {
    left: 12px;
    right: 60px;
  }
}
</style>

