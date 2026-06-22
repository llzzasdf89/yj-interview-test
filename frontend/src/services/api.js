import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const message = err.response?.data?.message || err.message || 'Unknown error'
    return Promise.reject(new Error(message))
  }
)

export const fetchOrders = () => api.get('/orders/')
export const fetchOrderDetail = (orderNo) => api.get(`/orders/${encodeURIComponent(orderNo)}`)
export const fetchTracking = (trackingRef) => api.get(`/tracking/${encodeURIComponent(trackingRef)}`)
