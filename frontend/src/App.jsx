import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { apiHealth } from './services/api'

import Dashboard         from './pages/Dashboard'
import Predictor         from './pages/Predictor'
import CampaignAnalytics from './pages/CampaignAnalytics'
import ModelInsights     from './pages/ModelInsights'
import CampaignExplorer  from './pages/CampaignExplorer'
import About             from './pages/About'
import NotFound          from './pages/NotFound'

const NAV = [
  {
    to: '/', label: 'Dashboard', end: true,
    icon: <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.4"/><rect x="9" y="1" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.4"/><rect x="1" y="9" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.4"/><rect x="9" y="9" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.4"/></svg>,
  },
  {
    to: '/predict', label: 'ROI Predictor',
    icon: <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.4"/><path d="M8 5v3l2 2" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>,
  },
  {
    to: '/analytics', label: 'Analytics',
    icon: <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 12l3.5-4 3 2.5L12 5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/><rect x="1" y="13" width="14" height="1.2" rx="0.6" fill="currentColor" opacity="0.3"/></svg>,
  },
  {
    to: '/model', label: 'Model Insights',
    icon: <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 1.5L14 5v6L8 14.5 2 11V5L8 1.5z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/><circle cx="8" cy="8" r="2" stroke="currentColor" strokeWidth="1.4"/></svg>,
  },
  {
    to: '/explorer', label: 'Campaign Explorer',
    icon: <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1.5" y="3" width="13" height="10" rx="1.5" stroke="currentColor" strokeWidth="1.4"/><path d="M1.5 6h13" stroke="currentColor" strokeWidth="1.2" opacity="0.5"/><path d="M5 9h6M5 11.5h4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/></svg>,
  },
  {
    to: '/about', label: 'About',
    icon: <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.4"/><path d="M8 7v5M8 5v.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>,
  },
]

function Sidebar({ connected, open, onClose }) {
  return (
    <>
      {/* Overlay — always in DOM on mobile, visibility controlled by CSS + open state */}
      <div
        className={`sidebar-overlay${open ? ' visible' : ''}`}
        onClick={onClose}
        aria-hidden="true"
      />
      <aside className={`sidebar${open ? ' open' : ''}`} aria-label="Main navigation">
        <div className="sidebar-logo">
          <div className="logo-row">
            <div className="logo-mark">IQ</div>
            <span className="logo-name">InfluenceIQ</span>
          </div>
          <div className="logo-tagline">Predict. Optimize. Influence.</div>
          <div className={`status-pill${connected === false ? ' offline' : ''}`}>
            {connected === null ? 'Connecting…' : connected ? 'Model Connected' : 'Backend Offline'}
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-label">Navigation</div>
          {NAV.map(n => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
              onClick={onClose}
            >
              <span className="nav-icon">{n.icon}</span>
              {n.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div>OLS · n = 147,000 campaigns</div>
          <div>R² = 0.3190 · Statsmodels 0.14</div>
        </div>
      </aside>
    </>
  )
}

export default function App() {
  const [connected,   setConnected]   = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    apiHealth()
      .then(() => setConnected(true))
      .catch(() => setConnected(false))
  }, [])

  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar connected={connected} open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <div className="mobile-header">
          <div className="logo-row" style={{ gap: 8 }}>
            <div className="logo-mark">IQ</div>
            <span className="logo-name">InfluenceIQ</span>
          </div>
          <button
            className="hamburger"
            onClick={() => setSidebarOpen(o => !o)}
            aria-label="Toggle navigation menu"
            aria-expanded={sidebarOpen}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            Menu
          </button>
        </div>

        <main className="main-content">
          <Routes>
            <Route path="/"          element={<Dashboard />} />
            <Route path="/predict"   element={<Predictor />} />
            <Route path="/analytics" element={<CampaignAnalytics />} />
            <Route path="/model"     element={<ModelInsights />} />
            <Route path="/explorer"  element={<CampaignExplorer />} />
            <Route path="/about"     element={<About />} />
            <Route path="*"          element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
