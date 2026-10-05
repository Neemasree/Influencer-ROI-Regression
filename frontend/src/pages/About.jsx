import { useEffect } from 'react'

export default function About() {
  useEffect(() => { document.title = 'About — InfluenceIQ' }, [])

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">About InfluenceIQ</h1>
        <p className="page-subtitle">Final year academic project — Statistical Analysis and Predictive Modelling</p>
      </div>

      {/* Hero card */}
      <div className="card" style={{ borderColor: 'var(--border-subtle)', background: 'linear-gradient(135deg, rgba(79,110,247,0.06) 0%, rgba(6,182,212,0.04) 100%)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16 }}>
          <div className="logo-mark" style={{ width: 40, height: 40, fontSize: '0.85rem' }}>IQ</div>
          <div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>InfluenceIQ</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Predict. Optimize. Influence.</div>
          </div>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.8, maxWidth: 680 }}>
          InfluenceIQ is a full-stack analytics platform built on top of a multiple linear regression model trained on 147,000 real influencer marketing campaigns. It predicts Return on Investment (ROI) from measurable campaign characteristics — before any money is spent.
        </p>
      </div>

      <div className="chart-grid">
        {/* Problem statement */}
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>Problem Statement</div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
            Most influencer marketing budget decisions rely on follower count and intuition. This project builds a data-driven regression model using measurable campaign characteristics to predict ROI — answering the question:
          </p>
          <div style={{ margin: '14px 0', padding: '12px 16px', background: 'var(--bg-base)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', fontStyle: 'italic', color: 'var(--accent-light)', fontSize: '0.85rem', lineHeight: 1.7 }}>
            "Can we predict whether an influencer marketing campaign will deliver good ROI before spending money?"
          </div>
        </div>

        {/* Tech stack */}
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>Technology Stack</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[
              { layer: 'ML / Statistics', tech: 'Python · Statsmodels OLS · SciPy · scikit-learn', color: 'var(--accent-light)' },
              { layer: 'Data Pipeline',   tech: 'Pandas · NumPy · openpyxl',                       color: 'var(--green-light)' },
              { layer: 'Backend API',     tech: 'Flask · Python 3 · REST JSON',                    color: 'var(--amber-light)' },
              { layer: 'Frontend',        tech: 'React 18 · Vite · Recharts · React Router',       color: 'var(--purple-light)' },
            ].map(t => (
              <div key={t.layer} style={{ display: 'flex', gap: 12, alignItems: 'flex-start', padding: '8px 0', borderBottom: '1px solid var(--border-light)' }}>
                <span style={{ fontSize: '0.7rem', fontWeight: 700, color: t.color, minWidth: 110, textTransform: 'uppercase', letterSpacing: '0.05em', paddingTop: 1 }}>{t.layer}</span>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{t.tech}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Dataset + methodology */}
      <div className="chart-grid">
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>Dataset</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {[
              ['Source',          'Publicly available — Kaggle'],
              ['Raw rows',        '150,000 campaigns'],
              ['Processed rows',  '147,000 (after outlier capping)'],
              ['Raw columns',     '10'],
              ['Final columns',   '16 (+ 4 engineered + Year + Month)'],
              ['Platforms',       'Instagram, YouTube, TikTok, Twitter'],
              ['Categories',      'Beauty, Tech, Fashion, Food, Fitness, Travel, Gaming'],
            ].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-light)', fontSize: '0.78rem' }}>
                <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>{k}</span>
                <span style={{ color: 'var(--text-secondary)' }}>{v}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>Feature Engineering</div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 12 }}>
            These four variables were not in the raw dataset — they were derived by this project.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[
              { name: 'Engagement Rate', formula: '(Engagements / Reach) × 100', unit: '%' },
              { name: 'Campaign Cost',   formula: '(Reach × Platform CPM) / 1000', unit: 'INR' },
              { name: 'Revenue',         formula: 'Product_Sales × Category_Avg_Unit_Value', unit: 'INR' },
              { name: 'ROI (target)',    formula: '(Revenue − Cost) / Cost', unit: 'ratio' },
            ].map(f => (
              <div key={f.name} style={{ background: 'var(--bg-base)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '10px 12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)' }}>{f.name}</span>
                  <span className="badge badge-blue">{f.unit}</span>
                </div>
                <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '0.72rem', color: 'var(--text-muted)' }}>{f.formula}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Model results */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Final Model Results</div>
          <span className="badge badge-green">Statsmodels OLS</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: 10, marginBottom: 16 }}>
          {[
            { label: 'R²',           value: '0.3190', color: 'var(--accent-light)' },
            { label: 'Adjusted R²',  value: '0.3190', color: 'var(--accent-light)' },
            { label: 'F-statistic',  value: '17,218', color: 'var(--green-light)' },
            { label: 'MAE',          value: '139.42', color: 'var(--amber-light)' },
            { label: 'RMSE',         value: '267.18', color: 'var(--amber-light)' },
            { label: 'Observations', value: '147,000', color: 'var(--cyan-light)' },
          ].map(m => (
            <div key={m.label} style={{ background: 'var(--bg-base)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '10px 12px' }}>
              <div style={{ fontSize: '0.62rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: 5 }}>{m.label}</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: m.color, fontFamily: 'JetBrains Mono, monospace' }}>{m.value}</div>
            </div>
          ))}
        </div>
        <div style={{ background: 'var(--bg-base)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '12px 16px', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
          <strong style={{ color: 'var(--text-primary)' }}>Regression equation:</strong>
          <div style={{ fontFamily: 'JetBrains Mono, monospace', marginTop: 8, lineHeight: 2.2, fontSize: '0.75rem' }}>
            <span style={{ color: 'var(--accent-light)' }}>ROI</span> = 161.8977
            <span style={{ color: 'var(--green-light)' }}> + 1.0914</span> × Engagement_Rate
            <span style={{ color: 'var(--red-light)' }}> − 0.00286</span> × Campaign_Cost
            <span style={{ color: 'var(--green-light)' }}> + 0.0567</span> × Product_Sales
            <span style={{ color: 'var(--text-muted)' }}> − 0.0088</span> × Campaign_Duration_Days
          </div>
        </div>
      </div>

      {/* Limitations */}
      <div className="card" style={{ marginBottom: 0 }}>
        <div className="card-title" style={{ marginBottom: 12 }}>Limitations &amp; Future Scope</div>
        <div className="chart-grid" style={{ marginBottom: 0 }}>
          <div>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: 10 }}>Known Limitations</div>
            {[
              'R² = 0.319 — unobserved factors account for ~68% of variance',
              'CPM and unit values are estimated assumptions, not invoice data',
              'Categorical variables not included in regression (EDA only)',
              'ROI residuals are not normally distributed (noted in diagnostics)',
            ].map((l, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 8, fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                <span style={{ color: 'var(--red-light)', flexShrink: 0, marginTop: 2 }}>—</span>
                {l}
              </div>
            ))}
          </div>
          <div>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: 10 }}>Future Scope</div>
            {[
              'One-hot encode Platform, Category, Campaign Type in regression',
              'Log-transform ROI to reduce right skew',
              'Explore polynomial and interaction terms',
              'Apply Ridge/Lasso regularisation and compare with OLS',
            ].map((l, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 8, fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                <span style={{ color: 'var(--green-light)', flexShrink: 0, marginTop: 2 }}>+</span>
                {l}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
