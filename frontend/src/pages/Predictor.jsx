import { useState, useEffect } from 'react'
import { apiPredict } from '../services/api'
import { fmtFixed, fmtINR, fmtROI, fmtNumber } from '../components/fmt'

const PLATFORMS  = ['Instagram', 'YouTube', 'TikTok', 'Twitter']
const CATEGORIES = ['Beauty', 'Tech', 'Fashion', 'Food', 'Fitness', 'Travel', 'Gaming']
const TYPES      = ['Brand Awareness', 'Product Launch', 'Giveaway', 'Seasonal Sale', 'Event Promotion']
const CPM = { Instagram: 150, YouTube: 120, TikTok: 100, Twitter: 80 }
const AVG = { Beauty: 1500, Tech: 5000, Fashion: 1200, Food: 300, Fitness: 800, Travel: 3000, Gaming: 1000 }

function roiLabel(roi) {
  if (roi >= 15) return { label: 'Exceptional Return', cls: 'badge-green',  bar: 95, color: 'var(--green-light)' }
  if (roi >= 8)  return { label: 'Strong Return',      cls: 'badge-green',  bar: 75, color: 'var(--green-light)' }
  if (roi >= 3)  return { label: 'Good Return',        cls: 'badge-blue',   bar: 55, color: 'var(--accent-light)' }
  if (roi >= 1)  return { label: 'Moderate Return',    cls: 'badge-amber',  bar: 35, color: 'var(--amber-light)' }
  if (roi >= 0)  return { label: 'Low Return',         cls: 'badge-amber',  bar: 18, color: 'var(--amber-light)' }
  return          { label: 'Negative ROI',             cls: 'badge-red',    bar: 5,  color: 'var(--red-light)' }
}

const INIT = {
  platform: 'Instagram', influencer_category: 'Beauty', campaign_type: 'Brand Awareness',
  estimated_reach: '', engagements: '', product_sales: '', campaign_duration_days: '',
}

function FieldGroup({ label, error, hint, children }) {
  return (
    <div className="form-group">
      <label className="form-label">{label}</label>
      {children}
      {error && <span className="form-error">{error}</span>}
      {hint && !error && <span className="form-hint">{hint}</span>}
    </div>
  )
}

export default function Predictor() {
  const [form,    setForm]    = useState(INIT)
  const [errors,  setErrors]  = useState({})
  const [loading, setLoading] = useState(false)
  const [result,  setResult]  = useState(null)
  const [apiErr,  setApiErr]  = useState(null)

  useEffect(() => { document.title = 'ROI Predictor — InfluenceIQ' }, [])

  const set = (k, v) => { setForm(f => ({ ...f, [k]: v })); setErrors(e => ({ ...e, [k]: null })) }

  function validate() {
    const e = {}
    const reach = Number(form.estimated_reach)
    const eng   = Number(form.engagements)
    const sales = Number(form.product_sales)
    const dur   = Number(form.campaign_duration_days)
    if (!reach || reach <= 0)      e.estimated_reach        = 'Must be greater than 0'
    if (isNaN(eng) || eng < 0)     e.engagements            = 'Cannot be negative'
    if (eng > reach && reach > 0)  e.engagements            = 'Cannot exceed estimated reach'
    if (isNaN(sales) || sales < 0) e.product_sales          = 'Cannot be negative'
    if (!dur || dur <= 0)          e.campaign_duration_days = 'Must be greater than 0'
    return e
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setLoading(true); setApiErr(null); setResult(null)
    try {
      const data = await apiPredict({
        platform:               form.platform,
        influencer_category:    form.influencer_category,
        campaign_type:          form.campaign_type,
        estimated_reach:        Number(form.estimated_reach),
        engagements:            Number(form.engagements),
        product_sales:          Number(form.product_sales),
        campaign_duration_days: Number(form.campaign_duration_days),
      })
      setResult(data)
    } catch (err) {
      setApiErr(err?.response?.data?.error || 'Prediction failed. Please check your inputs and try again.')
    } finally {
      setLoading(false)
    }
  }

  const reach = Number(form.estimated_reach) || 0
  const eng   = Number(form.engagements) || 0
  const sales = Number(form.product_sales) || 0
  const engRate     = reach > 0 ? (eng / reach) * 100 : 0
  const costPreview = reach > 0 ? (reach * (CPM[form.platform] || 0)) / 1000 : 0
  const revPreview  = sales * (AVG[form.influencer_category] || 0)

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">ROI Predictor</h1>
        <p className="page-subtitle">Enter campaign parameters to get an OLS regression prediction with 95% confidence interval</p>
      </div>

      <div className="predictor-layout">
        {/* ── Left: Form ── */}
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div>
              <div className="card-title">Campaign Parameters</div>
              <div className="card-subtitle">All fields required — computed features use training-identical formulas</div>
            </div>
            <span className="badge badge-blue">OLS Model</span>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-section-label">Campaign</div>
            <div className="form-grid" style={{ marginBottom: 16 }}>
              <FieldGroup label="Platform">
                <select className="form-control" value={form.platform} onChange={e => set('platform', e.target.value)}>
                  {PLATFORMS.map(p => <option key={p}>{p}</option>)}
                </select>
              </FieldGroup>
              <FieldGroup label="Influencer Category">
                <select className="form-control" value={form.influencer_category} onChange={e => set('influencer_category', e.target.value)}>
                  {CATEGORIES.map(c => <option key={c}>{c}</option>)}
                </select>
              </FieldGroup>
              <FieldGroup label="Campaign Type">
                <select className="form-control" value={form.campaign_type} onChange={e => set('campaign_type', e.target.value)}>
                  {TYPES.map(t => <option key={t}>{t}</option>)}
                </select>
              </FieldGroup>
            </div>

            <div className="form-section-label">Audience</div>
            <div className="form-grid" style={{ marginBottom: 16 }}>
              <FieldGroup label="Estimated Reach" error={errors.estimated_reach}>
                <input className={`form-control${errors.estimated_reach ? ' error' : ''}`} type="number" min="1" placeholder="e.g. 500,000"
                  value={form.estimated_reach} onChange={e => set('estimated_reach', e.target.value)} />
              </FieldGroup>
              <FieldGroup label="Engagements" error={errors.engagements}
                hint={reach > 0 && eng >= 0 && !errors.engagements ? `Engagement rate: ${fmtFixed(engRate, 2)}%` : null}>
                <input className={`form-control${errors.engagements ? ' error' : ''}`} type="number" min="0" placeholder="e.g. 42,500"
                  value={form.engagements} onChange={e => set('engagements', e.target.value)} />
              </FieldGroup>
            </div>

            <div className="form-section-label">Business</div>
            <div className="form-grid" style={{ marginBottom: 20 }}>
              <FieldGroup label="Product Sales (units)" error={errors.product_sales}>
                <input className={`form-control${errors.product_sales ? ' error' : ''}`} type="number" min="0" placeholder="e.g. 800"
                  value={form.product_sales} onChange={e => set('product_sales', e.target.value)} />
              </FieldGroup>
              <FieldGroup label="Campaign Duration (days)" error={errors.campaign_duration_days}>
                <input className={`form-control${errors.campaign_duration_days ? ' error' : ''}`} type="number" min="1" placeholder="e.g. 14"
                  value={form.campaign_duration_days} onChange={e => set('campaign_duration_days', e.target.value)} />
              </FieldGroup>
            </div>

            {apiErr && <div className="error-banner" style={{ marginBottom: 16 }}>{apiErr}</div>}

            <div style={{ display: 'flex', gap: 10 }}>
              <button type="submit" className="btn btn-primary" disabled={loading} style={{ flex: 1 }}>
                {loading
                  ? <><span className="spinner" style={{ width: 15, height: 15, borderWidth: 2 }} /> Predicting…</>
                  : <>
                      <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.4"/><path d="M7 4.5v2.5l1.5 1.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>
                      Predict ROI
                    </>
                }
              </button>
              <button type="button" className="btn btn-secondary"
                onClick={() => { setForm(INIT); setResult(null); setErrors({}); setApiErr(null) }}>
                Reset
              </button>
            </div>
          </form>
        </div>

        {/* ── Right: Preview / Result ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Live computed features */}
          <div className="card" style={{ marginBottom: 0 }}>
            <div className="card-title" style={{ marginBottom: 12 }}>Computed Features</div>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 14, lineHeight: 1.6 }}>
              Calculated live using the same formulas as the training pipeline.
            </p>
            {[
              { label: 'Engagement Rate',   value: reach > 0 ? fmtFixed(engRate, 4) + '%' : '—',  color: 'var(--green-light)' },
              { label: 'Campaign Cost',     value: reach > 0 ? fmtINR(costPreview) : '—',          color: 'var(--amber-light)' },
              { label: 'Est. Revenue',      value: sales > 0 ? fmtINR(revPreview) : '—',           color: 'var(--cyan-light)' },
              { label: `CPM (${form.platform})`,              value: `₹${CPM[form.platform]}/1K`,                    color: 'var(--text-secondary)' },
              { label: `Avg Unit (${form.influencer_category})`, value: `₹${fmtNumber(AVG[form.influencer_category], 0)}`, color: 'var(--text-secondary)' },
            ].map(item => (
              <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border-light)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{item.label}</span>
                <span style={{ fontSize: '0.82rem', fontWeight: 600, color: item.color, fontFamily: 'JetBrains Mono, monospace' }}>{item.value}</span>
              </div>
            ))}
          </div>

          {/* Model formula */}
          <div className="card" style={{ marginBottom: 0 }}>
            <div className="card-title" style={{ marginBottom: 10 }}>Model Formula</div>
            <div className="equation-box" style={{ fontSize: '0.75rem', lineHeight: 2 }}>
              <div className="eq-line"><span className="eq-target">ROI</span><span className="eq-const"> = 161.8977</span></div>
              <div className="eq-line"><span className="eq-pos">+ 1.0914</span><span className="eq-feature"> × Engagement_Rate</span></div>
              <div className="eq-line"><span className="eq-neg">− 0.00286</span><span className="eq-feature"> × Campaign_Cost</span></div>
              <div className="eq-line"><span className="eq-pos">+ 0.0567</span><span className="eq-feature"> × Product_Sales</span></div>
              <div className="eq-line"><span className="eq-nsig">− 0.0088</span><span className="eq-nsig"> × Duration</span><span className="badge badge-amber" style={{ fontSize: '0.6rem', marginLeft: 6 }}>n.s.</span></div>
            </div>
          </div>

          {/* Empty state before prediction */}
          {!result && !loading && (
            <div className="card" style={{ marginBottom: 0 }}>
              <div className="empty-prediction">
                <div className="empty-prediction-icon">
                  <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="9" stroke="var(--accent-light)" strokeWidth="1.5"/><path d="M11 7v4l2.5 2.5" stroke="var(--accent-light)" strokeWidth="1.5" strokeLinecap="round"/></svg>
                </div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>Ready to predict</div>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: 220 }}>
                  Fill in the campaign parameters and click Predict ROI to see your result with a 95% prediction interval.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Full-width Result ── */}
      {result && <PredictionResult result={result} />}
    </div>
  )
}

function PredictionResult({ result }) {
  const roi  = result.predicted_roi
  const info = roiLabel(roi)
  const ret  = result.estimated_return

  return (
    <div className="prediction-result">
      {/* Header row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 20 }}>
        <div>
          <div style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: 6 }}>Predicted ROI</div>
          <div className="predicted-roi-value" style={{ color: info.color }}>{fmtROI(roi)}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: 6 }}>
            95% Prediction Interval: [{fmtFixed(result.ci_lower_95, 2)}, {fmtFixed(result.ci_upper_95, 2)}]
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-end' }}>
          <span className={`badge ${info.cls}`} style={{ fontSize: '0.78rem', padding: '4px 12px' }}>{info.label}</span>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            {result.inputs.platform} · {result.inputs.influencer_category} · {result.inputs.campaign_type}
          </div>
        </div>
      </div>

      {/* Gauge */}
      <div style={{ marginBottom: 22 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: 5 }}>
          <span>Performance Score</span><span>{info.bar}%</span>
        </div>
        <div className="roi-gauge-track">
          <div className="roi-gauge-fill" style={{ width: `${info.bar}%`, background: `linear-gradient(90deg, var(--accent), ${info.color})` }} />
        </div>
      </div>

      {/* Metrics */}
      <div className="prediction-meta-grid" style={{ marginBottom: 22 }}>
        {[
          { label: 'Engagement Rate', value: fmtFixed(result.engagement_rate, 4) + '%', color: 'var(--green-light)' },
          { label: 'Campaign Cost',   value: fmtINR(result.campaign_cost),              color: 'var(--amber-light)' },
          { label: 'Est. Revenue',    value: fmtINR(result.estimated_revenue),          color: 'var(--cyan-light)' },
          { label: 'Est. Net Return', value: fmtINR(ret),                               color: ret >= 0 ? 'var(--green-light)' : 'var(--red-light)' },
        ].map(item => (
          <div key={item.label} className="prediction-meta-item">
            <div className="prediction-meta-label">{item.label}</div>
            <div className="prediction-meta-value" style={{ color: item.color }}>{item.value}</div>
          </div>
        ))}
      </div>

      {/* Why this prediction */}
      <div style={{ borderTop: '1px solid var(--border)', paddingTop: 20 }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 14 }}>
          Why this prediction?
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(210px, 1fr))', gap: 10 }}>
          {[
            {
              label: 'Engagement Rate',
              value: fmtFixed(result.engagement_rate, 2) + '%',
              impact: result.engagement_rate > 5 ? 'positive' : 'neutral',
              note: result.engagement_rate > 5
                ? 'Above-average engagement — strongest positive driver (+1.0914 per %)'
                : 'Moderate engagement — limited positive contribution',
            },
            {
              label: 'Campaign Cost',
              value: fmtINR(result.campaign_cost),
              impact: 'negative',
              note: 'Higher cost reduces ROI — coefficient is −0.00286 per INR',
            },
            {
              label: 'Product Sales',
              value: fmtNumber(result.inputs.product_sales, 0) + ' units',
              impact: result.inputs.product_sales > 500 ? 'positive' : 'neutral',
              note: 'Each additional sale adds +0.0567 to predicted ROI',
            },
            {
              label: 'Campaign Duration',
              value: result.inputs.campaign_duration_days + ' days',
              impact: 'ns',
              note: 'Not statistically significant (p = 0.916) — minimal effect on ROI',
            },
          ].map(f => (
            <div key={f.label} style={{ background: 'var(--bg-base)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '12px 14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{f.label}</span>
                <span className={`badge ${f.impact === 'positive' ? 'badge-green' : f.impact === 'negative' ? 'badge-red' : f.impact === 'ns' ? 'badge-amber' : 'badge-blue'}`}>
                  {f.impact === 'ns' ? 'n.s.' : f.impact}
                </span>
              </div>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'JetBrains Mono, monospace', marginBottom: 5 }}>{f.value}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{f.note}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
