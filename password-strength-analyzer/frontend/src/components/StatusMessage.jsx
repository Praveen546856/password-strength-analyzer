export default function StatusMessage({ status, error }) {
  if (status === 'loading') {
    return <p className="status loading" role="status">Analyzing password…</p>
  }
  if (status === 'error') {
    return <p className="status error" role="alert">{error}</p>
  }
  if (status === 'success') {
    return <p className="status success" role="status">Analysis complete.</p>
  }
  return null
}
