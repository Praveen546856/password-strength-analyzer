import { useRef, useState } from 'react'
import { analyzePassword } from './api'
import PasswordInput from './components/PasswordInput'
import StrengthMeter from './components/StrengthMeter'
import ChecksList from './components/ChecksList'
import Suggestions from './components/Suggestions'
import StatusMessage from './components/StatusMessage'

const MAX_LENGTH = 128

export default function App() {
  // The password lives ONLY in this React state. No localStorage / sessionStorage.
  const [password, setPassword] = useState('')
  const [result, setResult] = useState(null)
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [error, setError] = useState('')
  const controllerRef = useRef(null)

  function handleChange(value) {
    setPassword(value)
    // Old result no longer matches the text, so remove it.
    setResult(null)
    setStatus('idle')
    setError('')
  }

  async function handleAnalyze(event) {
    event.preventDefault()
    if (status === 'loading') return
    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller

    setStatus('loading')
    setError('')
    try {
      const data = await analyzePassword(password, controller.signal)
      setResult(data)
      setStatus('success')
    } catch (err) {
      if (err.name === 'AbortError') return
      setResult(null)
      setError(err.message)
      setStatus('error')
    }
  }

  function handleReset() {
    controllerRef.current?.abort()
    setPassword('')
    setResult(null)
    setStatus('idle')
    setError('')
  }

  return (
    <main className="app">
      <header className="header">
        <p className="eyebrow">Cybersecurity internship project</p>
        <h1>Password Strength Analyzer</h1>
        <p className="lead">
          Check how strong a password is and get practical tips to improve it. The password is
          sent only to the backend running on your own computer, analyzed in memory, and never
          stored or logged.
        </p>
      </header>

      <form className="card" onSubmit={handleAnalyze} autoComplete="off">
        <PasswordInput
          value={password}
          onChange={handleChange}
          maxLength={MAX_LENGTH}
          disabled={status === 'loading'}
        />
        <div className="actions">
          <button type="submit" className="btn primary" disabled={status === 'loading'}>
            {status === 'loading' ? 'Analyzing…' : 'Analyze'}
          </button>
          <button type="button" className="btn" onClick={handleReset}>
            Reset
          </button>
        </div>
      </form>

      <StatusMessage status={status} error={error} />

      {status === 'success' && result && (
        <section className="results" aria-label="Analysis results">
          <StrengthMeter result={result} />
          <div className="grid">
            <ChecksList checks={result.checks} />
            <Suggestions reasons={result.reasons} suggestions={result.suggestions} />
          </div>
          <p className="disclaimer">{result.disclaimer}</p>
        </section>
      )}

      <footer className="footer">
        Local development tool. Do not enter passwords you currently use for important accounts
        into any tool you do not fully trust.
      </footer>
    </main>
  )
}
