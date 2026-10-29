# Password Strength Analyzer and Security Assistant

A local web application that estimates how strong a password is and gives practical suggestions to improve it. Built as a cybersecurity internship project.

## Problem statement
Many people pick passwords that satisfy simple rules ("one capital, one number") but are still easy to guess, such as `Password1!`. This project shows how to evaluate passwords using real attack patterns instead of only counting character types.

## Objectives
- Evaluate password length, character types, common passwords, repeats, sequences and dictionary weaknesses
- Provide a transparent, documented scoring system with a clear explanation of each rating
- Expose the analysis through a validated REST API
- Provide a responsive React dashboard
- Protect password privacy (nothing stored, nothing logged, nothing sent to third parties)
- Cover the logic and API with automated tests

## Features
- Show/hide and clear buttons; the field is never pre-filled
- Five levels: Very Weak, Weak, Moderate, Strong, Very Strong, with a 0-100 score
- 8-point characteristics checklist and a "why this rating" explanation
- Recommendations (longer passphrase, avoid sequences, no reuse, password manager, MFA)
- Loading, success and error states; Reset button clears everything

## Technologies
| Part | Tools |
|---|---|
| Backend | Python 3, FastAPI, Uvicorn, Pydantic, zxcvbn, Pytest |
| Frontend | React, Vite, JavaScript, HTML, CSS |
| Environment | Windows 11, VS Code, PowerShell |

## Architecture
```
React + Vite (http://localhost:5173)  --POST /api/analyze-password-->  FastAPI (http://127.0.0.1:8000)
                                      <------- JSON result ---------   analyzer.py (in memory only)
```
- **Frontend**: collects input, calls the API, shows results. The password exists only in React state.
- **Backend**: validates the request (Pydantic), runs `analyze_password`, returns JSON. No database, no file writes.
- **Why a backend at all?** To demonstrate REST API design, validation, regex and automated testing. In a production system, analysis should preferably run **locally in the browser** so the password never crosses a network. Here it only travels to your own computer (127.0.0.1).

## Folder structure
```
password-strength-analyzer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, CORS, routes, safe error handlers
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── analyzer.py          # scoring logic
│   │   └── common_passwords.py  # small list of well-known weak passwords
│   ├── tests/
│   │   ├── test_analyzer.py
│   │   └── test_api.py
│   ├── pytest.ini
│   ├── requirements.txt
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── components/ (PasswordInput, StrengthMeter, ChecksList, Suggestions, StatusMessage)
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html, package.json, vite.config.js, .gitignore
├── docs/screenshots/
├── README.md
├── VIVA_PREPARATION.md
└── .gitignore
```

## Installation (Windows 11, PowerShell)
Open the project folder in VS Code.

**1. Check tools**
```powershell
python --version
node --version
npm --version
```
You need Python 3.10+ and Node.js 20+ (install from python.org and nodejs.org if missing).

**2. Backend setup** (Terminal 1)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
If activation is blocked, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again.

**3. Frontend setup** (Terminal 2)
```powershell
cd frontend
npm install
```
(The Vite project is already created; you do not need `npm create vite`.)

## Running
**Terminal 1 (backend):**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
**Terminal 2 (frontend):**
```powershell
cd frontend
npm run dev
```
Open **http://localhost:5173** in your browser. API docs (auto-generated): http://127.0.0.1:8000/docs

## Scoring system
1. **Base score** = `min(100, log10(estimated guesses) / 12 * 100)` using the zxcvbn library, which knows common words, names, keyboard patterns, dates, repeats and l33t substitutions.
2. **Caps** then lower the score (never raise it):

| Condition | Maximum score |
|---|---|
| Empty | 0 |
| In common-password list | 5 |
| Shorter than 8 characters | 25 |
| Contains sequence (abcd, 1234, qwer) | 35 |
| Contains 3+ repeated characters | 45 |
| Shorter than 12 characters | 70 |

3. **Label**: 0-19 Very Weak, 20-39 Weak, 40-59 Moderate, 60-79 Strong, 80-100 Very Strong.

## API documentation
**POST /api/analyze-password**

Request:
```json
{ "password": "example" }
```
`password` is a string, 0 to 128 characters. Extra fields are rejected.

Response (200):
```json
{
  "score": 12,
  "strength": "Very Weak",
  "checks": {
    "length": false, "uppercase": false, "lowercase": true, "number": false,
    "special_character": false, "not_common": true, "no_sequence": true, "no_repeats": true
  },
  "reasons": ["Only 7 characters long (very short)."],
  "suggestions": ["Use a longer password or a passphrase of 12+ characters."],
  "length": 7,
  "estimated_guesses_log10": 3.2,
  "disclaimer": "This score is a heuristic estimate..."
}
```
(Values above are illustrative.)

Errors: `422` invalid request (generic message, never echoes the input), `500` internal error (generic message, no stack trace), `405` wrong method.

**GET /api/health** returns `{"status": "ok"}`.

## Testing
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
```
Read the result: each dot / `PASSED` is a passing test; `FAILED` shows the assertion that broke; the last line shows totals. Tests cover empty, short, lowercase-only, mixed-case, numbers and symbols, passphrases, common passwords, sequences, repeats, spaces, Unicode, invalid API requests, CORS and non-leaking error messages. All test passwords are invented samples.

## Security considerations
- No database; nothing written to disk
- Request bodies are never logged; the unexpected-error handler logs only the exception type
- Validation errors are replaced with a generic message so the password is not echoed
- CORS allows only `http://localhost:5173` and `http://127.0.0.1:5173`
- No third-party API calls (for example no breach-lookup service)
- Frontend never uses localStorage or sessionStorage; Reset clears the field and result
- Intended for **local development only**. Deploying it would additionally require HTTPS, rate limiting and a review of hosting security.
- Do not type passwords you use for important accounts into any tool you do not fully trust.

## Limitations
- The score is a heuristic estimate, not a cryptographic measurement
- It cannot know whether a password appeared in a data breach
- The built-in common-password list is small (zxcvbn's dictionaries add coverage but are not exhaustive)
- Sequence detection covers straight runs and common keyboard rows, not every pattern
- Not designed for production or multi-user deployment

## Future enhancements
- Fully client-side analysis (bundle zxcvbn in the browser) so passwords never leave the page
- Optional offline breached-password check using k-anonymity hashes
- Rate limiting, HTTPS and containerization for deployment
- Passphrase generator and internationalization

## Screenshots
Run the app, then take your own screenshots (Windows: `Win + Shift + S`) and save them in `docs/screenshots/`, for example `home.png`, `weak-result.png`, `strong-result.png`. Then add to this README:
```markdown
![Home screen](docs/screenshots/home.png)
```

## GitHub
```powershell
git init
git add .
git status
git commit -m "Initial commit: Password Strength Analyzer with FastAPI backend, React frontend and tests"
git branch -M main
git remote add origin https://github.com/<your-username>/password-strength-analyzer.git
git push -u origin main
```
Suggested repository description: *"Local password strength analyzer using FastAPI, zxcvbn and React, with privacy-focused design and automated tests."*
Before committing, run `git status` and confirm `venv/`, `node_modules/` and `.env` files are not listed.

## Troubleshooting
| Problem | Fix |
|---|---|
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `python` not found | Reinstall Python and tick "Add python.exe to PATH", or try `py` |
| `uvicorn` not recognized | Activate the venv first |
| Port 8000 or 5173 in use | Close the other program; the frontend must stay on 5173 (CORS) |
| Frontend says "Cannot reach the local backend" | Start the backend in Terminal 1 |
| `ModuleNotFoundError: app` | Run commands from the `backend` folder |
