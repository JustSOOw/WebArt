<!--
 * @Author: Furdow wang22338014@gmail.com
 * @Date: 2025-03-04 13:43:22
 * @LastEditors: Furdow wang22338014@gmail.com
 * @LastEditTime: 2025-03-04 15:18:46
 * @FilePath: \WebArt\CustomOptions.vue
 * @Description: 
 * 
 * Copyright (c) 2025 by Furdow, All Rights Reserved. 
-->
<template>
  <div class="custom-options">
    <!-- 风格参数调节 -->
    <el-slider 
      v-model="distortion"
      :min="0"
      :max="10"
      show-stops
      label="扭曲程度"
    ></el-slider>

    <!-- 字体上传 -->
    <el-upload
      action="/api/upload-font"
      :limit="1"
      :on-success="handleFontUpload"
    >
      <el-button type="primary">点击上传字体文件（.ttf）</el-button>
    </el-upload>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const distortion = ref(5)
const customFont = ref(null)

const handleFontUpload = (response) => {
  customFont.value = response.fontPath
}
</script>