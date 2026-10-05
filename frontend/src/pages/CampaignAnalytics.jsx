import { useState, useEffect } from 'react'
import { useFetch } from '../hooks/useFetch'
import {
  apiPlatform, apiCategory, apiCampaignType, apiMonthly,
  apiRoiHistogram, apiScatter,
} from '../services/api'
import { Loading, ErrorView } from '../components/StateViews'
import { fmtFixed, fmtROI, fmtINR, fmtNumber, tickFmtROI } from '../components/fmt'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, Cell, Legend, Area, AreaChart,
} from 'recharts'

const COLORS = ['#4f6ef7','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#f97316']

const TABS = ['Overview', 'Platforms', 'Categories', 'Campaign Types', 'Relationships']

function ChartTip({ active, payload, label, fmt = fmtROI }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      {label && <div className="chart-tooltip-label">{label}</div>}
      {payload.map((p, i) => (
        <div key={i} className="chart-tooltip-row">
          <span className="chart-tooltip-dot" style={{ background: p.color }} />
          <span style={{ color: 'var(--text-secondary)' }}>{p.name}:</span>
          <span style={{ color: p.color, fontWeight: 600 }}>
            {p.name?.includes('Eng') ? fmtFixed(p.value, 2) + '%' : fmt(p.value)}
          </span>
        </div>
      ))}
    </div>
  )
}

function ScatterPanel({ xCol, yCol, color, xLabel, xFmt }) {
  const { data, loading } = useFetch(() => apiScatter({ x_col: xCol, y_col: yCol, sample_n: 2500 }), [xCol])
  if (loading) return <div style={{ height: 240 }}><Loading text="" /></div>
  return (
    <ResponsiveContainer width="100%" height={240}>
      <ScatterChart margin={{ top: 4, right: 8, bottom: 28, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="x" type="number" tickFormatter={xFmt || (v => v)}
          tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false}
          label={{ value: xLabel, position: 'insideBottom', offset: -14, fill: 'var(--text-muted)', fontSize: 11 }} />
        <YAxis dataKey="y" type="number" tickFormatter={tickFmtROI}
          tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip cursor={{ strokeDasharray: '3 3' }} content={({ active, payload }) => {
          if (!active || !payload?.length) return null
          return (
            <div className="chart-tooltip">
              <div className="chart-tooltip-row">
                <span style={{ color: 'var(--text-secondary)' }}>{xLabel}:</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                  {xFmt ? xFmt(payload[0]?.value) : fmtFixed(payload[0]?.value, 2)}
                </span>
              </div>
              <div className="chart-tooltip-row">
                <span className="chart-tooltip-dot" style={{ background: color }} />
                <span style={{ color: 'var(--text-secondary)' }}>ROI:</span>
                <span style={{ color, fontWeight: 600 }}>{fmtROI(payload[1]?.value)}</span>
              </div>
            </div>
          )
        }} />
        <Scatter data={data?.data || []} fill={color} fillOpacity={0.28} />
      </ScatterChart>
    </ResponsiveContainer>
  )
}

export default function CampaignAnalytics() {
  const [tab, setTab] = useState('Overview')

  const { data: platform,     loading: pL, error: pE, retry: pR } = useFetch(apiPlatform,     [])
  const { data: category,     loading: cL }             = useFetch(apiCategory,     [])
  const { data: campaignType, loading: tL }             = useFetch(apiCampaignType, [])
  const { data: monthly,      loading: mL }             = useFetch(apiMonthly,      [])
  const { data: histogram,    loading: hL }             = useFetch(() => apiRoiHistogram({ bins: 50 }), [])

  useEffect(() => { document.title = 'Analytics — InfluenceIQ' }, [])

  if (pL && tab === 'Overview') return <Loading text="Loading analytics…" />
  if (pE) return <ErrorView message={pE} onRetry={pR} />

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Analytics</h1>
        <p className="page-subtitle">Interactive analysis across 147,000 campaigns — platform, category, trend, and scatter analysis</p>
      </div>

      <div className="tab-bar">
        {TABS.map(t => (
          <button key={t} className={`tab-btn${tab === t ? ' active' : ''}`} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </div>

      {/* ── Overview ── */}
      {tab === 'Overview' && (
        <>
          <div className="chart-grid">
            <div className="chart-card">
              <div className="chart-title">ROI Distribution</div>
              <div className="chart-desc">Frequency distribution across all campaigns (1st–99th percentile cap)</div>
              {hL ? <Loading text="" /> : (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={histogram} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                    <XAxis dataKey="label" tick={false} axisLine={false} />
                    <YAxis tickFormatter={v => fmtNumber(v, 0)} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip content={({ active, payload }) => {
                      if (!active || !payload?.length) return null
                      const d = payload[0]?.payload
                      return (
                        <div className="chart-tooltip">
                          <div className="chart-tooltip-label">ROI: {d?.label}</div>
                          <div className="chart-tooltip-row">
                            <span className="chart-tooltip-dot" style={{ background: '#4f6ef7' }} />
                            <span style={{ color: 'var(--text-secondary)' }}>Count:</span>
                            <span style={{ color: '#4f6ef7', fontWeight: 600 }}>{fmtNumber(d?.count, 0)}</span>
                          </div>
                        </div>
                      )
                    }} />
                    <Bar dataKey="count" name="Campaigns" fill="#4f6ef7" fillOpacity={0.75} radius={[2,2,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="chart-card">
              <div className="chart-title">Monthly ROI Trend</div>
              <div className="chart-desc">Average and median ROI per calendar month</div>
              {mL ? <Loading text="" /> : (
                <ResponsiveContainer width="100%" height={240}>
                  <AreaChart data={monthly} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                    <defs>
                      <linearGradient id="avgGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#4f6ef7" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#4f6ef7" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                    <XAxis dataKey="month_name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tickFormatter={tickFmtROI} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<ChartTip />} />
                    <Legend wrapperStyle={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }} />
                    <Area type="monotone" dataKey="average_roi" name="Avg ROI" stroke="#4f6ef7" strokeWidth={2} fill="url(#avgGrad)" dot={{ fill: '#4f6ef7', r: 3, strokeWidth: 0 }} activeDot={{ r: 5 }} />
                    <Line type="monotone" dataKey="median_roi" name="Median ROI" stroke="#10b981" strokeWidth={2} strokeDasharray="5 3" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </>
      )}

      {/* ── Platforms ── */}
      {tab === 'Platforms' && (
        <div className="chart-grid cols-1">
          <div className="chart-card">
            <div className="chart-title">Platform Comparison</div>
            <div className="chart-desc">Average ROI and engagement rate by social media platform</div>
            {pL ? <Loading text="" /> : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={platform} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="platform" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis yAxisId="roi" tickFormatter={tickFmtROI} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis yAxisId="eng" orientation="right" tickFormatter={v => fmtFixed(v, 1) + '%'} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<ChartTip />} />
                  <Legend wrapperStyle={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }} />
                  <Bar yAxisId="roi" dataKey="average_roi" name="Avg ROI" radius={[4,4,0,0]} maxBarSize={56}>
                    {platform?.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                  <Bar yAxisId="eng" dataKey="average_engagement_rate" name="Avg Eng Rate" fill="#f59e0b" fillOpacity={0.5} radius={[4,4,0,0]} maxBarSize={56} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      )}

      {/* ── Categories ── */}
      {tab === 'Categories' && (
        <div className="chart-grid cols-1">
          <div className="chart-card">
            <div className="chart-title">Category Comparison</div>
            <div className="chart-desc">Average ROI by influencer content category</div>
            {cL ? <Loading text="" /> : (
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={category} layout="vertical" margin={{ top: 4, right: 24, bottom: 4, left: 72 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                  <XAxis type="number" tickFormatter={tickFmtROI} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="category" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} width={72} axisLine={false} tickLine={false} />
                  <Tooltip content={<ChartTip />} />
                  <Bar dataKey="average_roi" name="Avg ROI" radius={[0,4,4,0]} maxBarSize={28}>
                    {category?.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      )}

      {/* ── Campaign Types ── */}
      {tab === 'Campaign Types' && (
        <div className="chart-grid cols-1">
          <div className="chart-card">
            <div className="chart-title">Campaign Type Analysis</div>
            <div className="chart-desc">Average ROI by campaign type</div>
            {tL ? <Loading text="" /> : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={campaignType} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="campaign_type" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tickFormatter={tickFmtROI} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<ChartTip />} />
                  <Bar dataKey="average_roi" name="Avg ROI" radius={[4,4,0,0]} maxBarSize={56}>
                    {campaignType?.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      )}

      {/* ── Relationships ── */}
      {tab === 'Relationships' && (
        <>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 14 }}>
            Scatter plots — 2,500 sampled campaigns per chart
          </div>
          <div className="chart-grid">
            <div className="chart-card">
              <div className="chart-title">Engagement Rate vs ROI</div>
              <div className="chart-desc">Strongest positive predictor — coef +1.0914</div>
              <ScatterPanel xCol="Engagement_Rate" yCol="ROI" color="#4f6ef7"
                xLabel="Engagement Rate (%)" xFmt={v => fmtFixed(v, 1) + '%'} />
            </div>
            <div className="chart-card">
              <div className="chart-title">Campaign Cost vs ROI</div>
              <div className="chart-desc">Negative association — coef −0.00286</div>
              <ScatterPanel xCol="Campaign_Cost" yCol="ROI" color="#ef4444"
                xLabel="Campaign Cost (INR)" xFmt={v => fmtINR(v)} />
            </div>
          </div>
          <div className="chart-grid">
            <div className="chart-card">
              <div className="chart-title">Product Sales vs ROI</div>
              <div className="chart-desc">Positive association — coef +0.0567</div>
              <ScatterPanel xCol="Product_Sales" yCol="ROI" color="#10b981"
                xLabel="Product Sales (units)" xFmt={v => fmtNumber(v, 0)} />
            </div>
            <div className="chart-card">
              <div className="chart-title">Campaign Duration vs ROI</div>
              <div className="chart-desc">Not statistically significant — p = 0.916</div>
              <ScatterPanel xCol="Campaign_Duration_Days" yCol="ROI" color="#8b5cf6"
                xLabel="Campaign Duration (days)" />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
