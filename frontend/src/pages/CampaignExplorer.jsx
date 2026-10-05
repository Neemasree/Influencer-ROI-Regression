import { useState, useCallback, useEffect } from 'react'
import { useFetch } from '../hooks/useFetch'
import { apiCampaigns, apiFilters, apiCampaignsExport } from '../services/api'
import { Loading, ErrorView, Empty } from '../components/StateViews'
import { fmtFixed, fmtROI, fmtINR, fmtNumber } from '../components/fmt'

function roiBadge(roi) {
  if (roi >= 10) return <span className="badge badge-green">{fmtROI(roi)}</span>
  if (roi >= 3)  return <span className="badge badge-blue">{fmtROI(roi)}</span>
  if (roi >= 0)  return <span className="badge badge-amber">{fmtROI(roi)}</span>
  return               <span className="badge badge-red">{fmtROI(roi)}</span>
}

function platformBadge(p) {
  const map = { Instagram: 'badge-purple', YouTube: 'badge-red', TikTok: 'badge-cyan', Twitter: 'badge-blue' }
  return <span className={`badge ${map[p] || 'badge-blue'}`}>{p}</span>
}

function TableSkeleton() {
  return (
    <div>
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} style={{ display: 'flex', gap: 12, padding: '11px 14px', borderBottom: '1px solid rgba(30,35,64,0.4)', opacity: 1 - i * 0.09 }}>
          {[14, 9, 10, 12, 8, 8, 9, 8, 6, 7].map((w, j) => (
            <div key={j} className="skeleton" style={{ height: 10, width: `${w}%`, borderRadius: 3 }} />
          ))}
        </div>
      ))}
    </div>
  )
}

const SORT_COLS = [
  { key: 'ROI',                    label: 'ROI'      },
  { key: 'Engagement_Rate',        label: 'Eng Rate' },
  { key: 'Campaign_Cost',          label: 'Cost'     },
  { key: 'Product_Sales',          label: 'Sales'    },
  { key: 'Campaign_Duration_Days', label: 'Duration' },
  { key: 'Estimated_Reach',        label: 'Reach'    },
]

const INIT_FILTERS = {
  platform: '', category: '', campaign_type: '', year: '', month: '',
  search: '', sort_by: 'ROI', sort_dir: 'desc', page: 1, limit: 25,
}

export default function CampaignExplorer() {
  const [filters, setFilters] = useState(INIT_FILTERS)

  useEffect(() => { document.title = 'Campaign Explorer — InfluenceIQ' }, [])

  const fetchFn = useCallback(
    () => apiCampaigns({ ...filters, page: filters.page }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(filters)]
  )

  const { data, loading, error, retry } = useFetch(fetchFn, [JSON.stringify(filters)])
  const { data: filterOpts }     = useFetch(apiFilters, [])

  const set     = (k, v) => setFilters(f => ({ ...f, [k]: v, page: 1 }))
  const setPage = (p)    => setFilters(f => ({ ...f, page: p }))
  const reset   = ()     => setFilters(INIT_FILTERS)

  const toggleSort = (col) => setFilters(f => ({
    ...f,
    sort_by:  col,
    sort_dir: f.sort_by === col && f.sort_dir === 'desc' ? 'asc' : 'desc',
    page: 1,
  }))

  const exportUrl = apiCampaignsExport({
    platform:      filters.platform      || undefined,
    category:      filters.category      || undefined,
    campaign_type: filters.campaign_type || undefined,
    year:          filters.year          || undefined,
    search:        filters.search        || undefined,
    sort_by:       filters.sort_by,
    sort_dir:      filters.sort_dir,
  })

  const rows       = data?.data        || []
  const total      = data?.total       || 0
  const totalPages = data?.total_pages || 1

  const SortTh = ({ col, label }) => (
    <th className={filters.sort_by === col ? 'sorted' : ''} onClick={() => toggleSort(col)}
      style={{ cursor: 'pointer', userSelect: 'none' }}>
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
        {label}
        {filters.sort_by === col
          ? <span style={{ color: 'var(--accent-light)', fontSize: '0.7rem' }}>{filters.sort_dir === 'desc' ? '↓' : '↑'}</span>
          : <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem', opacity: 0.4 }}>↕</span>
        }
      </span>
    </th>
  )

  const hasFilters = filters.platform || filters.category || filters.campaign_type || filters.year || filters.search

  return (
    <div>
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Campaign Explorer</h1>
            <p className="page-subtitle">Browse, filter, sort, and export all 147,000 processed campaigns</p>
          </div>
          <a href={exportUrl} download="campaigns_export.csv" className="btn btn-secondary btn-sm"
            style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path d="M6.5 1v8M3.5 6.5l3 3 3-3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M1 10.5h11" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
            </svg>
            Export CSV
          </a>
        </div>
      </div>

      {/* Filter bar */}
      <div className="filter-bar">
        <div className="form-group" style={{ flex: 2, minWidth: 160 }}>
          <label className="form-label">Search</label>
          <input className="form-control" placeholder="Campaign ID, platform…"
            value={filters.search} onChange={e => set('search', e.target.value)} />
        </div>
        <div className="form-group">
          <label className="form-label">Platform</label>
          <select className="form-control" value={filters.platform} onChange={e => set('platform', e.target.value)}>
            <option value="">All</option>
            {filterOpts?.platforms?.map(p => <option key={p}>{p}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Category</label>
          <select className="form-control" value={filters.category} onChange={e => set('category', e.target.value)}>
            <option value="">All</option>
            {filterOpts?.categories?.map(c => <option key={c}>{c}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Campaign Type</label>
          <select className="form-control" value={filters.campaign_type} onChange={e => set('campaign_type', e.target.value)}>
            <option value="">All</option>
            {filterOpts?.campaign_types?.map(t => <option key={t}>{t}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Year</label>
          <select className="form-control" value={filters.year} onChange={e => set('year', e.target.value)}>
            <option value="">All</option>
            {filterOpts?.years?.map(y => <option key={y}>{y}</option>)}
          </select>
        </div>
        {hasFilters && (
          <div className="form-group" style={{ justifyContent: 'flex-end' }}>
            <label className="form-label" style={{ opacity: 0 }}>x</label>
            <button className="btn btn-ghost btn-sm" onClick={reset}
              style={{ border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
              Clear filters
            </button>
          </div>
        )}
      </div>

      {/* Table card */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="card-header" style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
          <div>
            <div className="card-title">Campaigns</div>
            <div className="card-subtitle">
              {loading ? 'Loading…' : `${fmtNumber(total, 0)} results`}
              {hasFilters && !loading && <span style={{ color: 'var(--accent-light)', marginLeft: 6 }}>· filtered</span>}
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <label className="form-label" style={{ margin: 0, whiteSpace: 'nowrap' }}>Per page</label>
            <select className="form-control" style={{ width: 72, padding: '5px 8px', fontSize: '0.8rem' }}
              value={filters.limit} onChange={e => set('limit', Number(e.target.value))}>
              {[10, 25, 50, 100].map(n => <option key={n}>{n}</option>)}
            </select>
          </div>
        </div>

        {error ? (
          <ErrorView message="Unable to load campaign data." onRetry={retry} />
        ) : (
          <>
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Campaign ID</th>
                    <th>Platform</th>
                    <th>Category</th>
                    <th>Type</th>
                    <SortTh col="Estimated_Reach"        label="Reach"    />
                    <SortTh col="Engagement_Rate"        label="Eng Rate" />
                    <SortTh col="Campaign_Cost"          label="Cost"     />
                    <SortTh col="Product_Sales"          label="Sales"    />
                    <SortTh col="Campaign_Duration_Days" label="Days"     />
                    <SortTh col="ROI"                    label="ROI"      />
                  </tr>
                </thead>
                <tbody>
                  {loading ? null : rows.length === 0 ? null : rows.map((r, i) => (
                    <tr key={r.Campaign_ID || i}>
                      <td className="mono" style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>{r.Campaign_ID}</td>
                      <td>{platformBadge(r.Platform)}</td>
                      <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{r.Influencer_Category}</td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{r.Campaign_Type}</td>
                      <td className="mono" style={{ color: 'var(--text-secondary)' }}>{fmtNumber(r.Estimated_Reach, 0)}</td>
                      <td className="mono" style={{ color: 'var(--amber-light)' }}>{fmtFixed(r.Engagement_Rate, 2)}%</td>
                      <td className="mono" style={{ color: 'var(--text-secondary)' }}>{fmtINR(r.Campaign_Cost)}</td>
                      <td className="mono" style={{ color: 'var(--text-secondary)' }}>{fmtNumber(r.Product_Sales, 0)}</td>
                      <td className="mono" style={{ color: 'var(--text-muted)' }}>{r.Campaign_Duration_Days}d</td>
                      <td>{roiBadge(r.ROI)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {loading && <TableSkeleton />}
              {!loading && rows.length === 0 && <Empty text="No campaigns match your filters. Try clearing some filters." />}
            </div>

            {!loading && rows.length > 0 && (
              <div className="pagination">
                <div className="pagination-info">
                  Page {data.page} of {totalPages} · {fmtNumber(total, 0)} total campaigns
                </div>
                <div className="pagination-controls">
                  <button className="page-btn" disabled={data.page <= 1} onClick={() => setPage(1)} aria-label="First page">«</button>
                  <button className="page-btn" disabled={data.page <= 1} onClick={() => setPage(data.page - 1)} aria-label="Previous page">‹</button>
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const start = Math.max(1, Math.min(data.page - 2, totalPages - 4))
                    const p = start + i
                    return p <= totalPages ? (
                      <button key={p} className={`page-btn${p === data.page ? ' active' : ''}`} onClick={() => setPage(p)}>{p}</button>
                    ) : null
                  })}
                  <button className="page-btn" disabled={data.page >= totalPages} onClick={() => setPage(data.page + 1)} aria-label="Next page">›</button>
                  <button className="page-btn" disabled={data.page >= totalPages} onClick={() => setPage(totalPages)} aria-label="Last page">»</button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
