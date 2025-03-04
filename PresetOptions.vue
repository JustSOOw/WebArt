<template>
  <div class="preset-options">
    <!-- 风格选择 -->
    <el-select v-model="style" placeholder="选择创像风格">
      <el-option
        v-for="item in presetStyles"
        :key="item.value"
        :label="item.label"
        :value="item.value"
      >
        <span>{{ item.label }}</span>
        <span class="demo-color" :style="{backgroundColor: item.color}"></span>
      </el-option>
    </el-select>

    <!-- 字体选择 -->
    <el-select v-model="font" placeholder="选择字体风格">
      <el-option
        v-for="font in presetFonts"
        :key="font.value"
        :label="font.label"
        :value="font.value"
      />
    </el-select>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const presetStyles = ref([
  { value: 'sakura', label: '樱花烂漫', color: '#FFB3BF' },
  { value: 'peace', label: '世界和平', color: '#A5D6A7' }
])

const presetFonts = ref([
  { value: 'ancient', label: '仿古风体' },
  { value: 'modern', label: '现代简约体' }
])

const style = ref('')
const font = ref('')
</script>