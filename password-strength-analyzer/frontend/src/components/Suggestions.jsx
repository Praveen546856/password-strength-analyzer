export default function Suggestions({ reasons, suggestions }) {
  return (
    <div className="card">
      <h2>Why this rating</h2>
      <ul className="plain">
        {reasons.map((r) => <li key={r}>{r}</li>)}
      </ul>
      <h2>Recommendations</h2>
      <ul className="plain">
        {suggestions.map((s) => <li key={s}>{s}</li>)}
      </ul>
    </div>
  )
}
