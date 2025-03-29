<!--
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-20 16:23:45
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-27 21:56:02
 * @FilePath: \WebArt\frontend\src\components\chat\ChatView.vue
 * @Description: 
 * 
 * Copyright (c) 2025 by Furdow, All Rights Reserved. 
-->
.main-container {
  height: 100vh;
  background-color: var(--background-color);
}

.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin: 20px;
  overflow: hidden;
}

.chat-display {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  background-color: #fff;
  overflow: hidden;
}

@media (max-width: 768px) {
  .chat-container {
    margin: 0;
    border-radius: 0;
  }
} 