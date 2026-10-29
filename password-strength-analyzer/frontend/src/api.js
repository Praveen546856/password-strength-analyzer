// The backend runs locally. Passwords are sent ONLY to this local address.
const API_URL = 'http://127.0.0.1:8000'

export async function analyzePassword(password, signal) {
  let response
  try {
    response = await fetch(`${API_URL}/api/analyze-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
      signal,
    })
  } catch (err) {
    if (err.name === 'AbortError') throw err
    throw new Error('Cannot reach the local backend. Is it running on port 8000?')
  }

  if (!response.ok) {
    let message = 'Something went wrong while analyzing the password.'
    try {
      const data = await response.json()
      if (data.detail && typeof data.detail === 'string') message = data.detail
    } catch {
      /* keep the generic message */
    }
    throw new Error(message)
  }
  return response.json()
}
