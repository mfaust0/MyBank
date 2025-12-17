import axios from 'axios'
import { useAuth } from '@/stores/auth.js'

const httpClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-type': 'application/json'
  }
})

// Intercettore di richiesta: aggiunge il token prima che la richiesta parta
httpClient.interceptors.request.use(
  (config) => {
    const authStore = useAuth()
    const token = authStore.token

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default httpClient
