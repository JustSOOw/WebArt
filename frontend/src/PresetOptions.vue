<template>
  <div class="preset-options">
    <div class="section-header">
      <el-icon><Collection /></el-icon>
      <span>预设模式</span>
    </div>
    
    <el-row :gutter="20" class="style-row">
      <el-col :xs="24" :sm="12" v-for="option in presetOptions" :key="option.id">
        <div
          class="style-card"
          :class="{ active: selectedOption === option }"
          @click="selectOption(option)"
        >
          <el-icon :size="32" class="style-icon">
            <component :is="option.icon" />
          </el-icon>
          <h3>{{ option.name }}</h3>
          <p>{{ option.description }}</p>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref } from 'vue'
import {
  Brush,
  Collection,
  Sunny,
  Star
} from '@element-plus/icons-vue'

export default {
  name: 'PresetOptions',
  components: {
    Brush,
    Collection,
    Sunny,
    Star
  },
  setup(props, { emit }) {
    const selectedOption = ref(null)
    const presetOptions = [
      {
        id: 1,
        name: '现代风格',
        description: '简洁现代的艺术风格',
        icon: 'Brush'
      },
      {
        id: 2,
        name: '传统风格',
        description: '传统经典的艺术表现',
        icon: 'Collection'
      },
      {
        id: 3,
        name: '极简风格',
        description: '简约而有力的表达',
        icon: 'Sunny'
      },
      {
        id: 4,
        name: '艺术风格',
        description: '大胆富有表现力的创意',
        icon: 'Star'
      }
    ]

    const selectOption = (option) => {
      selectedOption.value = option
      emit('option-selected', option)
    }

    return {
      selectedOption,
      presetOptions,
      selectOption
    }
  }
}
</script>

<style scoped>
.preset-options {
  width: 100%;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 0 0 20px 0;
  margin: 0;
  position: relative;
  z-index: 1;
  min-height: 400px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;
}

.section-header .el-icon {
  font-size: 24px;
  color: #409EFF;
}

.style-row {
  padding: 0 20px;
  display: flex;
  flex-wrap: wrap;
}

.style-card {
  background: white;
  border: 1px solid #ebeef5;
  height: 100%;
  min-height: 150px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 24px;
  text-align: center;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.style-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.style-card.active {
  border: 2px solid #409EFF;
  background: rgba(64, 158, 255, 0.05);
}

.style-icon {
  margin-bottom: 16px;
  color: #409EFF;
  font-size: 40px !important;
}

h3 {
  margin: 12px 0 8px;
  font-size: 18px;
  color: #2c3e50;
  font-weight: 600;
}

p {
  margin: 0;
  font-size: 14px;
  color: #5c6b7f;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .style-card {
    margin-bottom: 16px;
    padding: 16px;
  }

  .style-icon {
    font-size: 32px !important;
  }

  h3 {
    font-size: 16px;
  }

  p {
    font-size: 12px;
  }
}
</style>