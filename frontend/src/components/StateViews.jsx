export function Loading({ text = 'Loading data…' }) {
  return (
    <div className="state-center">
      <div className="spinner" />
      {text && <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{text}</p>}
    </div>
  )
}

export function ErrorView({ message, onRetry }) {
  const friendly = message?.includes('Network Error') || message?.includes('ECONNREFUSED')
    ? 'Cannot reach the backend server. Make sure it is running on port 5000.'
    : message?.includes('timeout')
    ? 'The request timed out. The server may be under load — please retry.'
    : message || 'An unexpected error occurred.'

  return (
    <div className="state-center">
      <div className="state-icon" style={{ background: 'var(--red-dim)', border: '1px solid rgba(239,68,68,0.2)' }}>
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="8.5" stroke="#ef4444" strokeWidth="1.5"/>
          <path d="M10 6v5M10 13.5v.5" stroke="#ef4444" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </div>
      <h3>Unable to load data</h3>
      <p>{friendly}</p>
      {onRetry && (
        <button className="btn btn-secondary btn-sm" onClick={onRetry} style={{ marginTop: 4 }}>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M1 6a5 5 0 105-5 5 5 0 00-3.5 1.4L1 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M1 1v3h3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Retry
        </button>
      )}
    </div>
  )
}

export function Empty({ text = 'No data available.' }) {
  return (
    <div className="state-center">
      <div className="state-icon" style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <rect x="3" y="5" width="14" height="11" rx="2" stroke="var(--text-muted)" strokeWidth="1.5"/>
          <path d="M7 9h6M7 12h4" stroke="var(--text-muted)" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </div>
      <h3 style={{ color: 'var(--text-secondary)' }}>No results</h3>
      <p>{text}</p>
    </div>
  )
}
