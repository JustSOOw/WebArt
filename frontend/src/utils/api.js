/*
 * @Author: JustSOOw wang813104@outlook.com
 * @Date: 2025-03-11 13:34:34
 * @LastEditors: JustSOOw wang813104@outlook.com
 * @LastEditTime: 2025-03-11 15:44:28
 * @FilePath: \WebArt\frontend\src\utils\api.js
 * @Description: 
 * 
 * Copyright (c) 2025 by Furdow, All Rights Reserved. 
 */
/**
 * API相关工具函数
 */

/**
 * 获取API基础URL
 * 根据环境确定API的基础URL
 * - 开发环境: 使用相对路径，通过代理转发
 * - 生产环境: 使用相对路径，依赖nginx配置
 * - Docker环境: 在开发环境下，可能需要使用完整URL（如果是直接访问容器）
 */
export const getApiBaseUrl = () => {
  // 默认使用相对路径，依赖代理或nginx配置
  return '/api'
}

/**
 * 构建完整的API URL
 * @param {string} path API路径，不包含/api前缀
 * @returns {string} 完整的API URL
 */
export const getApiUrl = (path) => {
  const baseUrl = getApiBaseUrl()
  // 确保path不以/开头，因为baseUrl已经包含了/
  const normalizedPath = path.startsWith('/') ? path.substring(1) : path
  return `${baseUrl}/${normalizedPath}`
} 