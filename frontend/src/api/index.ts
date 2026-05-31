import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：自动注入 auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截器：统一错误处理
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (!error.response) {
      return Promise.reject(error)
    }

    const { status, data } = error.response

    switch (status) {
      case 401:
        localStorage.removeItem('access_token')
        window.location.href = '/login'
        break
      case 403:
        console.error('无权限')
        break
      case 404:
        console.error('资源不存在')
        break
      case 422:
        console.error('请求参数错误:', data.errors || data.detail)
        break
      case 500:
      case 503:
        console.error('服务暂时不可用，请稍后重试')
        break
    }

    return Promise.reject(error)
  },
)

export default apiClient
