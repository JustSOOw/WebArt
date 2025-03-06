<template>
  <div class="custom-options">
    <div class="section-header">
      <el-icon><Edit /></el-icon>
      <span>自定义模式</span>
    </div>

    <div class="form-container">
      <el-form :model="form" label-position="top">
        <el-form-item label="生成风格描述">
          <el-input
            v-model="form.style"
            type="textarea"
            :rows="3"
            placeholder="描述您想要的艺术风格..."
          />
        </el-form-item>

        <el-form-item label="选择颜色方案">
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

        <el-form-item label="附加效果">
          <el-select
            v-model="form.effects"
            multiple
            placeholder="选择效果"
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
            应用自定义风格
            <el-icon class="el-icon--right"><Check /></el-icon>
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
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
      { label: '模糊效果', value: 'blur' },
      { label: '渐变叠加', value: 'gradient' },
      { label: '纹理', value: 'texture' },
      { label: '发光', value: 'glow' }
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
  width: 100%;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 0 0 20px 0;
  margin: 0;
  position: relative;
  z-index: 1;
  min-height: 400px;
  display: flex;
  flex-direction: column;
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

.form-container {
  padding: 0 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.form-container .el-form {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.color-picker {
  margin-right: 16px;
  margin-bottom: 16px;
}

.apply-button {
  width: 100%;
  max-width: 480px;
  margin: 32px auto 0;
  height: 56px;
  font-size: 18px;
  border-radius: 28px;
  font-weight: 500;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #2c3e50;
  font-size: 16px;
  margin-bottom: 8px;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  box-shadow: none;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover),
:deep(.el-textarea__inner:hover) {
  border-color: #409EFF;
}

:deep(.el-textarea__inner) {
  padding: 12px;
  font-size: 14px;
  line-height: 1.6;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-select .el-input__wrapper) {
  padding: 0 12px;
}

:deep(.el-select-dropdown__item) {
  padding: 8px 16px;
}

@media (max-width: 768px) {
  .apply-button {
    height: 48px;
    font-size: 16px;
  }
  
  :deep(.el-form-item__label) {
    font-size: 14px;
  }
}
</style>