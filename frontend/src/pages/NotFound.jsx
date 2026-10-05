import { useEffect } from 'react'
import { Link } from 'react-router-dom'

export default function NotFound() {
  useEffect(() => { document.title = '404 — InfluenceIQ' }, [])
  return (
    <div className="state-center" style={{ minHeight: '60vh' }}>
      <div style={{ fontSize: '3.5rem', fontWeight: 800, color: 'var(--border)', letterSpacing: '-0.05em', lineHeight: 1 }}>404</div>
      <h3 style={{ fontSize: '1rem', marginTop: 8 }}>Page not found</h3>
      <p>The page you're looking for doesn't exist or has been moved.</p>
      <Link to="/" className="btn btn-primary btn-sm" style={{ marginTop: 8 }}>
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
          <path d="M6.5 1L1 6.5l5.5 5.5M1 6.5h11" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        Back to Dashboard
      </Link>
    </div>
  )
}
