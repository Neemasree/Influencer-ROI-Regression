export function Skeleton({ width = '100%', height = 16, radius = 4, style = {} }) {
  return (
    <div className="skeleton" style={{ width, height, borderRadius: radius, ...style }} />
  )
}

export function SkeletonCard({ lines = 3 }) {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <Skeleton height={14} width="40%" />
      <Skeleton height={32} width="60%" />
      {lines > 2 && <Skeleton height={12} width="30%" />}
    </div>
  )
}

export function SkeletonChart({ height = 240 }) {
  return (
    <div className="chart-card">
      <Skeleton height={14} width="35%" style={{ marginBottom: 8 }} />
      <Skeleton height={10} width="55%" style={{ marginBottom: 20 }} />
      <Skeleton height={height} radius={6} />
    </div>
  )
}

export function SkeletonTable({ rows = 8 }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      <div style={{ display: 'flex', gap: 12, padding: '10px 14px', borderBottom: '1px solid var(--border)' }}>
        {[20, 12, 14, 12, 10, 10, 10, 10].map((w, i) => (
          <Skeleton key={i} height={10} width={`${w}%`} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{ display: 'flex', gap: 12, padding: '10px 14px', borderBottom: '1px solid rgba(46,50,72,0.4)' }}>
          {[20, 12, 14, 12, 10, 10, 10, 10].map((w, j) => (
            <Skeleton key={j} height={10} width={`${w}%`} style={{ opacity: 1 - i * 0.08 }} />
          ))}
        </div>
      ))}
    </div>
  )
}
