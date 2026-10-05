import { useEffect } from 'react'
import { useFetch } from '../hooks/useFetch'
import { apiModel } from '../services/api'
import { Loading, ErrorView } from '../components/StateViews'
import { fmtFixed, fmtNumber, fmtInt } from '../components/fmt'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts'

function MetricCard({ label, value, meta, color }) {
  return (
    <div style={{ background: 'var(--bg-base)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '14px 16px' }}>
      <div style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: '1.35rem', fontWeight: 700, color, fontFamily: 'JetBrains Mono, monospace', letterSpacing: '-0.03em', marginBottom: 3 }}>{value}</div>
      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{meta}</div>
    </div>
  )
}

const PIPELINE_STEPS = [
  { label: 'Campaign Data',         desc: '147,000 rows × 16 columns',       highlight: false },
  { label: 'Feature Engineering',   desc: 'Engagement Rate, Cost, Revenue',   highlight: false },
  { label: 'OLS Regression',        desc: 'statsmodels.api.OLS + sm.add_constant()', highlight: true },
  { label: 'ROI Prediction',        desc: 'Fitted values on all observations', highlight: false },
  { label: '95% Prediction Interval', desc: 'get_prediction().summary_frame()', highlight: false },
]

export default function ModelInsights() {
  const { data: model, loading, error, retry } = useFetch(apiModel, [])

  useEffect(() => { document.title = 'Model Insights — InfluenceIQ' }, [])

  if (loading) return <Loading text="Loading model metrics…" />
  if (error)   return <ErrorView message={error} onRetry={retry} />

  const coefData = model.coefficients.map(c => ({
    name:        c.predictor.replace(/_/g, ' '),
    coefficient: c.coefficient,
    sig:         c.significance,
    p:           c.p_value,
    interp:      c.interpretation,
  }))

  const metrics = [
    { label: 'R²',           value: fmtFixed(model.r_squared, 4),          meta: 'Goodness of fit',          color: 'var(--accent-light)' },
    { label: 'Adjusted R²',  value: fmtFixed(model.adjusted_r_squared, 4), meta: 'Penalised for predictors', color: 'var(--accent-light)' },
    { label: 'F-statistic',  value: fmtNumber(model.f_statistic, 0),       meta: 'p < 0.001',                color: 'var(--green-light)' },
    { label: 'MAE',          value: fmtFixed(model.mae, 2),                 meta: 'Mean absolute error',      color: 'var(--amber-light)' },
    { label: 'RMSE',         value: fmtFixed(model.rmse, 2),                meta: 'Root mean squared error',  color: 'var(--amber-light)' },
    { label: 'AIC',          value: fmtInt(model.aic),                   meta: 'Akaike info criterion',    color: 'var(--purple-light)' },
    { label: 'BIC',          value: fmtInt(model.bic),                   meta: 'Bayesian info criterion',  color: 'var(--purple-light)' },
    { label: 'Observations', value: fmtNumber(model.observations, 0),       meta: 'Training rows',            color: 'var(--cyan-light)' },
  ]

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Model Insights</h1>
        <p className="page-subtitle">OLS regression diagnostics, coefficients, and statistical interpretation</p>
      </div>

      {/* Model identity */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div className="card-title" style={{ fontSize: '1rem' }}>{model.algorithm}</div>
            <div className="card-subtitle" style={{ marginTop: 4 }}>
              Library: {model.library} · Target: <span style={{ color: 'var(--accent-light)' }}>{model.target}</span> · Features: {model.features.join(', ')}
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <span className="badge badge-green">p &lt; 0.001</span>
            <span className="badge badge-blue">n = {fmtNumber(model.observations, 0)}</span>
            <span className="badge badge-purple">OLS</span>
          </div>
        </div>
      </div>

      {/* Metric cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 12, marginBottom: 24 }}>
        {metrics.map(m => <MetricCard key={m.label} {...m} />)}
      </div>

      {/* Two-column: equation + pipeline */}
      <div className="chart-grid" style={{ marginBottom: 24 }}>
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div className="card-title">Regression Equation</div>
            <span className="badge badge-blue">OLS</span>
          </div>
          <div className="equation-box">
            <div className="eq-line">
              <span className="eq-target">ROI</span>
              <span className="eq-const"> = {fmtFixed(model.equation.intercept, 4)}</span>
            </div>
            <div className="eq-line">
              <span className="eq-pos">+ {fmtFixed(model.equation.Engagement_Rate, 4)}</span>
              <span className="eq-feature"> × Engagement_Rate</span>
            </div>
            <div className="eq-line">
              <span className="eq-neg">− {Math.abs(model.equation.Campaign_Cost).toFixed(5)}</span>
              <span className="eq-feature"> × Campaign_Cost</span>
            </div>
            <div className="eq-line">
              <span className="eq-pos">+ {fmtFixed(model.equation.Product_Sales, 4)}</span>
              <span className="eq-feature"> × Product_Sales</span>
            </div>
            <div className="eq-line">
              <span className="eq-nsig">− {Math.abs(model.equation.Campaign_Duration_Days).toFixed(4)}</span>
              <span className="eq-nsig"> × Campaign_Duration_Days</span>
              <span className="badge badge-amber" style={{ fontSize: '0.6rem', marginLeft: 8 }}>n.s.</span>
            </div>
          </div>
          <div style={{ marginTop: 14, padding: '10px 14px', background: 'var(--bg-base)', borderRadius: 'var(--radius-sm)', fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
            Coefficients represent the estimated change in ROI per one-unit increase in each predictor, holding others constant. These are statistical associations, not causal claims.
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-title" style={{ marginBottom: 16 }}>How the Model Works</div>
          <div className="pipeline">
            {PIPELINE_STEPS.map((step, i) => (
              <div key={i} className="pipeline-step">
                <div className={`pipeline-node${step.highlight ? ' highlight' : ''}`}>
                  <div style={{ fontWeight: 600 }}>{step.label}</div>
                  <div style={{ fontSize: '0.68rem', color: step.highlight ? 'var(--accent-light)' : 'var(--text-muted)', marginTop: 2, fontWeight: 400 }}>{step.desc}</div>
                </div>
                {i < PIPELINE_STEPS.length - 1 && <div className="pipeline-arrow">↓</div>}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Coefficient bar chart */}
      <div className="chart-card" style={{ marginBottom: 20 }}>
        <div className="chart-title">Regression Coefficients</div>
        <div className="chart-desc">Positive values increase ROI; negative values decrease it. Grey = not statistically significant.</div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={coefData} layout="vertical" margin={{ top: 4, right: 60, bottom: 4, left: 130 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
            <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} width={130} axisLine={false} tickLine={false} />
            <ReferenceLine x={0} stroke="var(--border)" strokeWidth={2} />
            <Tooltip content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const d = payload[0]?.payload
              return (
                <div className="chart-tooltip" style={{ maxWidth: 280 }}>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>{d.name}</div>
                  <div style={{ color: d.coefficient >= 0 ? 'var(--green-light)' : 'var(--red-light)' }}>Coefficient: {fmtFixed(d.coefficient, 6)}</div>
                  <div style={{ color: 'var(--text-secondary)' }}>p-value: {d.p < 0.001 ? '< 0.001' : fmtFixed(d.p, 4)}</div>
                  <div style={{ color: 'var(--text-muted)', marginTop: 4, whiteSpace: 'normal', lineHeight: 1.5 }}>{d.interp}</div>
                </div>
              )
            }} />
            <Bar dataKey="coefficient" name="Coefficient" radius={[0, 4, 4, 0]} maxBarSize={28}>
              {coefData.map((d, i) => (
                <Cell key={i} fill={d.sig === 'ns' ? 'var(--text-muted)' : d.coefficient >= 0 ? 'var(--green-light)' : 'var(--red-light)'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Coefficient table */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">Coefficient Table</div>
          <span className="badge badge-blue">Statsmodels OLS</span>
        </div>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Predictor</th>
                <th>Coefficient</th>
                <th>Std Error</th>
                <th>t-stat</th>
                <th>p-value</th>
                <th>95% CI</th>
                <th>Sig</th>
              </tr>
            </thead>
            <tbody>
              {model.coefficients.map(c => (
                <tr key={c.predictor}>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{c.predictor}</td>
                  <td className={`mono ${c.coefficient >= 0 ? 'coef-positive' : 'coef-negative'}`}>
                    {c.coefficient >= 0 ? '+' : ''}{fmtFixed(c.coefficient, 6)}
                  </td>
                  <td className="mono" style={{ color: 'var(--text-secondary)' }}>{fmtFixed(c.std_error, 6)}</td>
                  <td className="mono" style={{ color: 'var(--text-secondary)' }}>{fmtFixed(c.t_statistic, 4)}</td>
                  <td className="mono" style={{ color: c.p_value < 0.05 ? 'var(--green-light)' : 'var(--amber-light)' }}>
                    {c.p_value < 0.001 ? '< 0.001' : fmtFixed(c.p_value, 4)}
                  </td>
                  <td className="mono" style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                    [{fmtFixed(c.ci_lower, 4)}, {fmtFixed(c.ci_upper, 4)}]
                  </td>
                  <td>
                    <span className={c.significance === 'ns' ? 'sig-ns' : 'sig-stars'}>{c.significance}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Interpretation cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 14 }}>
        {model.coefficients.map(c => (
          <div key={c.predictor} className="card" style={{
            marginBottom: 0,
            borderColor: c.significance === 'ns'
              ? 'var(--border)'
              : c.coefficient >= 0 ? 'rgba(16,185,129,0.25)' : 'rgba(239,68,68,0.25)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
              <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-primary)' }}>
                {c.predictor.replace(/_/g, ' ')}
              </div>
              <span className={`badge ${c.significance === 'ns' ? 'badge-amber' : c.coefficient >= 0 ? 'badge-green' : 'badge-red'}`}>
                {c.significance === 'ns' ? 'Not Significant' : c.coefficient >= 0 ? 'Positive' : 'Negative'}
              </span>
            </div>
            <div className={`mono ${c.coefficient >= 0 ? 'coef-positive' : 'coef-negative'}`}
              style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8, letterSpacing: '-0.03em' }}>
              {c.coefficient >= 0 ? '+' : ''}{fmtFixed(c.coefficient, 4)}
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{c.interpretation}</p>
            <div style={{ marginTop: 10, fontSize: '0.68rem', color: 'var(--text-muted)' }}>
              p = {c.p_value < 0.001 ? '< 0.001' : fmtFixed(c.p_value, 4)} · {c.significance}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
