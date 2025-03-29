<template>
  <div class="model-selector">
    <el-select
      v-model="selectedModel"
      :disabled="disabled"
      @change="handleModelChange"
      default-first-option
      size="small"
      popper-class="model-popper"
    >
      <el-option
        v-for="model in availableModels"
        :key="model.id"
        :label="model.name"
        :value="model.id"
      >
        <div class="model-option">
          <span class="model-name">{{ model.name }}</span>
          <span class="model-capabilities">
            <el-tag 
              v-for="capability in model.capabilities" 
              :key="capability"
              size="small"
              :type="getCapabilityType(capability)"
            >
              {{ getCapabilityName(capability) }}
            </el-tag>
          </span>
        </div>
      </el-option>
    </el-select>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'ModelSelector',
  props: {
    model: {
      type: String,
      required: true
    },
    availableModels: {
      type: Array,
      required: true
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['model-change'],
  setup(props, { emit }) {
    const selectedModel = ref(props.model)
    
    // 监听model属性变化
    watch(() => props.model, (newValue) => {
      selectedModel.value = newValue
    })
    
    // 获取能力标签类型
    const getCapabilityType = (capability) => {
      const typeMap = {
        text: 'primary',
        image: 'success',
        file: 'warning'
      }
      return typeMap[capability] || 'info'
    }
    
    // 获取能力名称
    const getCapabilityName = (capability) => {
      const nameMap = {
        text: '文本',
        image: '图像',
        file: '文件'
      }
      return nameMap[capability] || capability
    }
    
    // 处理模型变化
    const handleModelChange = (value) => {
      emit('model-change', value)
    }
    
    return {
      selectedModel,
      getCapabilityType,
      getCapabilityName,
      handleModelChange
    }
  }
}
</script>

<style scoped>
.model-selector {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  display: inline-block;
  width: 160px;
}

.model-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-width: 120px;
}

.model-name {
  font-weight: 500;
}

.model-capabilities {
  display: flex;
  gap: 4px;
}

:deep(.el-select) {
  width: 160px;
}

:deep(.el-select .el-input__wrapper) {
  background-color: #fff;
  padding: 1px 6px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/* 确保下拉框不会太宽 */
:deep(.el-select .el-select__popper) {
  width: auto !important;
  max-width: 200px !important;
}

@media (max-width: 768px) {
  .model-selector {
    top: 12px;
  }
  
  :deep(.el-select) {
    width: 160px;
  }
  
  .model-option {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
