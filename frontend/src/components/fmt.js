/** Format large numbers: 147000 → 147K, 1500000 → 1.5M */
export function fmtNumber(n, decimals = 1) {
  if (n === null || n === undefined) return '—'
  if (Math.abs(n) >= 1_000_000) return (n / 1_000_000).toFixed(decimals) + 'M'
  if (Math.abs(n) >= 1_000)     return (n / 1_000).toFixed(decimals) + 'K'
  return Number(n).toLocaleString()
}

/** Format a raw integer with locale commas — for AIC, BIC, observation counts */
export function fmtInt(n) {
  if (n === null || n === undefined) return '—'
  return Math.round(Number(n)).toLocaleString()
}

/** Format a float to fixed decimals */
export function fmtFixed(n, d = 4) {
  if (n === null || n === undefined) return '—'
  return Number(n).toFixed(d)
}

/** Format currency in INR */
export function fmtINR(n) {
  if (n === null || n === undefined) return '—'
  if (Math.abs(n) >= 1_000_000) return '₹' + (n / 1_000_000).toFixed(2) + 'M'
  if (Math.abs(n) >= 1_000)     return '₹' + (n / 1_000).toFixed(1) + 'K'
  return '₹' + Number(n).toFixed(2)
}

/** Format ROI as a ratio to 2 decimal places */
export function fmtROI(n) {
  if (n === null || n === undefined) return '—'
  return Number(n).toFixed(2)
}

/** Format percentage */
export function fmtPct(n, d = 2) {
  if (n === null || n === undefined) return '—'
  return Number(n).toFixed(d) + '%'
}

/** Recharts tick formatter — compact */
export const tickFmt = (v) => fmtNumber(v, 0)
export const tickFmtROI = (v) => fmtFixed(v, 1)
