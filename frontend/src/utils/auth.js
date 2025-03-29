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
  const token = getToken()
  const user = getCurrentUser()
  
  // 确保令牌和用户信息都存在
  if (!token || !user) {
    return false
  }
  
  // 检查用户信息是否有效
  if (!user.id || !user.username) {
    // 如果用户信息不完整，清理存储
    removeToken()
    removeCurrentUser()
    return false
  }
  
  // 可以增加令牌过期检查（如果令牌包含过期时间）
  
  return true
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
  const baseUrl = 'http://localhost';
  const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
  
  // 准备请求选项
  const fetchOptions = { ...options };
  fetchOptions.headers = fetchOptions.headers || {};
  
  // 添加认证头
  const token = localStorage.getItem('auth_token');
  if (token) {
    fetchOptions.headers['Authorization'] = `Bearer ${token}`;
  }
  
  // 添加标准内容类型（如果未指定）
  if (!fetchOptions.headers['Content-Type'] && fetchOptions.method !== 'GET') {
    fetchOptions.headers['Content-Type'] = 'application/json';
  }
  
  try {
    console.log(`发送请求到: ${fullUrl}`, fetchOptions);
    const response = await fetch(fullUrl, fetchOptions);
    
    // 处理认证错误
    if (response.status === 401) {
      console.warn('认证失败，清除登录状态');
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_info');
      
      // 如果是API请求，不要重定向（让调用方处理）
      if (url.includes('/api/')) {
        return response;
      }
      
      // 对于页面请求，重定向到登录页
      window.location.href = '/login';
      return response;
    }
    
    return response;
  } catch (error) {
    console.error(`请求失败: ${fullUrl}`, error);
    throw error;
  }
} 