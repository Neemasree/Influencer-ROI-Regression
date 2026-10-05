import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({ baseURL: BASE, timeout: 30000 })

// ── helper ─────────────────────────────────────────────────────────────────
const get  = (url, params) => api.get(url, { params }).then(r => r.data)
const post = (url, data)   => api.post(url, data).then(r => r.data)

// ── endpoints ──────────────────────────────────────────────────────────────
export const apiHealth        = ()       => get('/health')
export const apiDashboard     = ()       => get('/dashboard')
export const apiModel         = ()       => get('/model')
export const apiFilters       = ()       => get('/filters')

export const apiPlatform      = ()       => get('/analytics/platform')
export const apiCategory      = ()       => get('/analytics/category')
export const apiCampaignType  = ()       => get('/analytics/campaign-type')
export const apiMonthly       = ()       => get('/analytics/monthly')
export const apiCorrelation   = ()       => get('/analytics/correlation')
export const apiScatter       = (params) => get('/analytics/scatter', params)
export const apiRoiHistogram  = (params) => get('/analytics/roi-histogram', params)

export const apiCampaigns     = (params) => get('/campaigns', params)
export const apiCampaignsExport = (params) => {
  const qs = new URLSearchParams(params).toString()
  return `${BASE}/campaigns/export?${qs}`
}

export const apiPredict       = (payload) => post('/predict', payload)
