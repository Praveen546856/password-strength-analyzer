const LEVELS = ['Very Weak', 'Weak', 'Moderate', 'Strong', 'Very Strong']

export default function StrengthMeter({ result }) {
  const level = LEVELS.indexOf(result.strength)
  return (
    <div className="card meter" data-level={level}>
      <div className="meter-top">
        <div>
          <p className="label">Strength</p>
          <p className="strength">{result.strength}</p>
        </div>
        <div className="score" aria-label={`Score ${result.score} out of 100`}>
          {result.score}
          <span>/100</span>
        </div>
      </div>
      <div
        className="bar"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={result.score}
        aria-label="Password strength score"
      >
        <div className="bar-fill" style={{ width: `${Math.max(result.score, 2)}%` }} />
      </div>
      <div className="segments" aria-hidden="true">
        {LEVELS.map((name, i) => (
          <span key={name} className={i <= level ? 'on' : ''}>{name}</span>
        ))}
      </div>
    </div>
  )
}
