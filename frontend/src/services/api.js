import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 45000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error.message ||
      'Request failed'

    return Promise.reject(new Error(message))
  }
)

export async function scanUrl(payload) {
  const { data } = await api.post('/api/scan/url', payload)
  return data
}

export async function scanEmail(payload) {
  const { data } = await api.post('/api/scan/email', payload)
  return data
}

export async function scanSms(payload) {
  const { data } = await api.post('/api/scan/sms', payload)
  return data
}

export async function getDashboard(userId) {
  const { data } = await api.get(`/api/dashboard/${userId}`)
  return data
}

export async function getEducation(userId) {
  const { data } = await api.get(`/api/education/${userId}`)
  return data
}

export default api
