import { useState } from 'react'

export default function PasswordInput({ value, onChange, maxLength, disabled }) {
  const [visible, setVisible] = useState(false)

  return (
    <div className="field">
      <label htmlFor="password-input">Password to analyze</label>
      <div className="input-row">
        <input
          id="password-input"
          type={visible ? 'text' : 'password'}
          value={value}
          maxLength={maxLength}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Type a password to test"
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck={false}
        />
        <button
          type="button"
          className="btn small"
          onClick={() => setVisible((v) => !v)}
          aria-pressed={visible}
        >
          {visible ? 'Hide' : 'Show'}
        </button>
        <button
          type="button"
          className="btn small"
          onClick={() => onChange('')}
          disabled={!value}
        >
          Clear
        </button>
      </div>
      <p className="hint">{value.length} / {maxLength} characters</p>
    </div>
  )
}
