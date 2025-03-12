/**
 * 认证相关工具函数
 */

/**
 * 获取存储的认证令牌
 * @returns {string|null} 认证令牌
 */
export const getToken = () => {
  return localStorage.getItem('auth_token')
}

/**
 * 设置认证令牌
 * @param {string} token 认证令牌
 */
export const setToken = (token) => {
  localStorage.setItem('auth_token', token)
}

/**
 * 移除认证令牌
 */
export const removeToken = () => {
  localStorage.removeItem('auth_token')
}

/**
 * 获取当前用户信息
 * @returns {Object|null} 用户信息
 */
export const getCurrentUser = () => {
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    try {
      return JSON.parse(userInfo)
    } catch (e) {
      console.error('解析用户信息失败', e)
      return null
    }
  }
  return null
}

/**
 * 设置当前用户信息
 * @param {Object} user 用户信息
 */
export const setCurrentUser = (user) => {
  localStorage.setItem('user_info', JSON.stringify(user))
}

/**
 * 移除当前用户信息
 */
export const removeCurrentUser = () => {
  localStorage.removeItem('user_info')
}

/**
 * 检查用户是否已登录
 * @returns {boolean} 是否已登录
 */
export const isAuthenticated = () => {
  return !!getToken() && !!getCurrentUser()
}

/**
 * 登出
 */
export const logout = () => {
  removeToken()
  removeCurrentUser()
}

/**
 * 获取认证请求头
 * @returns {Object} 请求头对象
 */
export const getAuthHeaders = () => {
  const token = getToken()
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

/**
 * 发送认证请求
 * @param {string} url 请求URL
 * @param {Object} options 请求选项
 * @returns {Promise} 请求Promise
 */
export const authFetch = async (url, options = {}) => {
  const headers = {
    ...options.headers,
    ...getAuthHeaders(),
    'Content-Type': 'application/json'
  }
  
  const response = await fetch(url, {
    ...options,
    headers
  })
  
  // 如果返回401未授权，清除认证信息
  if (response.status === 401) {
    logout()
    throw new Error('登录已过期，请重新登录')
  }
  
  return response
} 