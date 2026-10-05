import { useState, useEffect, useRef, useCallback } from 'react'

export function useFetch(fn, deps = []) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)
  const [retryCount, setRetryCount] = useState(0)
  const mounted = useRef(true)

  useEffect(() => {
    mounted.current = true
    setLoading(true)
    setError(null)

    fn()
      .then(d  => { if (mounted.current) { setData(d); setLoading(false) } })
      .catch(e => { if (mounted.current) { setError(e?.response?.data?.error || e.message); setLoading(false) } })

    return () => { mounted.current = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, retryCount])

  const retry = useCallback(() => setRetryCount(c => c + 1), [])

  return { data, loading, error, retry }
}
