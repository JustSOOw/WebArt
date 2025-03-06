<template>
  <el-card class="custom-options">
    <template #header>
      <div class="card-header">
        <el-icon><Edit /></el-icon>
        <span>Custom Style</span>
      </div>
    </template>

    <el-form :model="form" label-position="top">
      <el-form-item label="Style Description">
        <el-input
          v-model="form.style"
          type="textarea"
          :rows="3"
          placeholder="Describe your desired artistic style..."
        />
      </el-form-item>

      <el-form-item label="Color Scheme">
        <el-color-picker
          v-model="form.primaryColor"
          class="color-picker"
          show-alpha
        />
        <el-color-picker
          v-model="form.secondaryColor"
          class="color-picker"
          show-alpha
        />
      </el-form-item>

      <el-form-item label="Additional Effects">
        <el-select
          v-model="form.effects"
          multiple
          placeholder="Select effects"
          style="width: 100%"
        >
          <el-option
            v-for="effect in availableEffects"
            :key="effect.value"
            :label="effect.label"
            :value="effect.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          @click="applyCustom"
          :disabled="!form.style"
          class="apply-button"
        >
          Apply Custom Style
          <el-icon class="el-icon--right"><Check /></el-icon>
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>
import { ref, reactive } from 'vue'
import { Edit, Check } from '@element-plus/icons-vue'

export default {
  name: 'CustomOptions',
  components: {
    Edit,
    Check
  },
  setup(props, { emit }) {
    const form = reactive({
      style: '',
      primaryColor: '#409EFF',
      secondaryColor: '#67C23A',
      effects: []
    })

    const availableEffects = [
      { label: 'Blur Effect', value: 'blur' },
      { label: 'Gradient Overlay', value: 'gradient' },
      { label: 'Texture', value: 'texture' },
      { label: 'Glow', value: 'glow' }
    ]

    const applyCustom = () => {
      emit('custom-applied', {
        style: form.style,
        colors: {
          primary: form.primaryColor,
          secondary: form.secondaryColor
        },
        effects: form.effects
      })
    }

    return {
      form,
      availableEffects,
      applyCustom
    }
  }
}
</script>

<style scoped>
.custom-options {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.color-picker {
  margin-right: 10px;
}

.apply-button {
  width: 100%;
  margin-top: 20px;
  height: 40px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #2c3e50;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  box-shadow: none;
  border: 1px solid #dcdfe6;
}

:deep(.el-input__wrapper:hover),
:deep(.el-textarea__inner:hover) {
  border-color: #409EFF;
}

:deep(.el-select) {
  width: 100%;
}
</style> 