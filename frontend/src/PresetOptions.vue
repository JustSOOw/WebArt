<template>
  <el-card class="preset-options">
    <template #header>
      <div class="card-header">
        <el-icon><Collection /></el-icon>
        <span>Preset Styles</span>
      </div>
    </template>
    
    <el-row :gutter="20">
      <el-col :span="12" v-for="option in presetOptions" :key="option.id">
        <el-card
          class="style-card"
          :class="{ active: selectedOption === option }"
          @click="selectOption(option)"
          :shadow="selectedOption === option ? 'always' : 'hover'"
        >
          <el-icon :size="32" class="style-icon">
            <component :is="option.icon" />
          </el-icon>
          <h3>{{ option.name }}</h3>
          <p>{{ option.description }}</p>
        </el-card>
      </el-col>
    </el-row>
  </el-card>
</template>

<script>
import { ref } from 'vue'
import {
  Brush,
  Picture,
  Sunny,
  Star
} from '@element-plus/icons-vue'

export default {
  name: 'PresetOptions',
  components: {
    Collection: Picture,
    Brush,
    Sunny,
    Star
  },
  setup(props, { emit }) {
    const selectedOption = ref(null)
    const presetOptions = [
      {
        id: 1,
        name: 'Modern',
        description: 'Clean and contemporary artistic style',
        icon: 'Brush'
      },
      {
        id: 2,
        name: 'Classic',
        description: 'Traditional and timeless approach',
        icon: 'Picture'
      },
      {
        id: 3,
        name: 'Minimalist',
        description: 'Simple yet powerful expressions',
        icon: 'Sunny'
      },
      {
        id: 4,
        name: 'Artistic',
        description: 'Bold and expressive creativity',
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
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.style-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  padding: 20px;
}

.style-card:hover {
  transform: translateY(-5px);
}

.style-card.active {
  border: 2px solid #409EFF;
  transform: translateY(-5px);
}

.style-icon {
  margin-bottom: 15px;
  color: #409EFF;
}

h3 {
  margin: 10px 0;
  color: #2c3e50;
}

p {
  font-size: 14px;
  color: #5c6b7f;
  margin: 0;
}
</style> 