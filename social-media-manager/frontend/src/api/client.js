import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

// Auth token injection
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Auth
export const authApi = {
  login: (email, password) => {
    const form = new FormData()
    form.append('username', email)
    form.append('password', password)
    return api.post('/auth/login', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  me: () => api.get('/auth/me'),
}

// Content
export const contentApi = {
  list: (params) => api.get('/content/', { params }),
  get: (id) => api.get(`/content/${id}`),
  pendingApproval: () => api.get('/content/pending-approval'),
  approve: (id, action) => api.post(`/content/${id}/approve`, action),
  stats: () => api.get('/content/stats/overview'),
  triggerGeneration: () => api.post('/content/generate/daily'),
}

// Knowledge Base
export const kbApi = {
  list: (category) => api.get('/knowledge-base/', { params: { category } }),
  categories: () => api.get('/knowledge-base/categories'),
  crawl: () => api.post('/knowledge-base/crawl'),
  seed: () => api.post('/knowledge-base/seed'),
}

// Analytics
export const analyticsApi = {
  overview: (days) => api.get('/analytics/overview', { params: { days } }),
  topContent: (limit, metric) => api.get('/analytics/top-content', { params: { limit, metric } }),
  calendar: (year, month) => api.get('/analytics/calendar', { params: { year, month } }),
}

// Credentials
export const credentialsApi = {
  list: () => api.get('/credentials/'),
  update: (service, value, extraData) => api.put(`/credentials/${service}`, { value, extra_data: extraData }),
  delete: (service) => api.delete(`/credentials/${service}`),
}
