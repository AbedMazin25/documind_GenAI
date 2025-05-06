import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// BUG: on 401, we refresh the token but never retry the original request
api.interceptors.response.use(
  (r) => r,
  async (error) => {
    if (error.response?.status === 401) {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        const { data } = await api.post('/auth/refresh', { refresh_token: refresh })
        localStorage.setItem('access_token', data.access_token)
      }
    }
    return Promise.reject(error)
  }
)

export default api
