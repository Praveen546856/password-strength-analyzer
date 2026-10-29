const LABELS = {
  length: 'At least 12 characters',
  uppercase: 'Has uppercase letters',
  lowercase: 'Has lowercase letters',
  number: 'Has numbers',
  special_character: 'Has special characters',
  not_common: 'Not a common password',
  no_sequence: 'No predictable sequence',
  no_repeats: 'No repeated characters',
}

export default function ChecksList({ checks }) {
  return (
    <div className="card">
      <h2>Characteristics</h2>
      <ul className="checks">
        {Object.entries(LABELS).map(([key, text]) => (
          <li key={key} className={checks[key] ? 'pass' : 'fail'}>
            <span className="icon" aria-hidden="true">{checks[key] ? '✓' : '✗'}</span>
            <span>{text}</span>
            <span className="sr-only">{checks[key] ? ' (passed)' : ' (not met)'}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
