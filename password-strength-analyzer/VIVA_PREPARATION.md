# Viva Preparation

## 1. Simple explanation
My project checks how hard a password would be to guess. You type a password, the React page sends it to a FastAPI server on my own laptop, the server scores it and explains why, and the page shows a rating with suggestions. Nothing is saved.

## 2. Architecture
Two parts: a React frontend (port 5173) and a FastAPI backend (port 8000). They talk using JSON over HTTP. CORS allows only the frontend origin. The backend has no database and no stored state.

## 3. Major files
- `backend/app/main.py`: creates the app, CORS, the `/api/analyze-password` route, and safe error handlers.
- `backend/app/schemas.py`: Pydantic models; validates that `password` is a string up to 128 characters and rejects extra fields.
- `backend/app/analyzer.py`: the scoring logic (zxcvbn base score + rule caps + checks + suggestions).
- `backend/app/common_passwords.py`: small list of well-known weak passwords.
- `backend/tests/`: Pytest tests for logic and API.
- `frontend/src/App.jsx`: state (password, result, status, error) and the analyze/reset handlers.
- `frontend/src/api.js`: the `fetch` call to the local backend.
- `frontend/src/components/*`: input, meter, checklist, suggestions, status message.

## 4. Algorithm
1. Compute 8 checks (length, upper, lower, number, special, not common, no sequence, no repeats).
2. Ask zxcvbn for estimated guesses; convert to 0-100 using log10(guesses)/12.
3. Apply caps for weak conditions (common password, short, sequence, repeat).
4. Map the score to a label; build reasons and suggestions.
It is an estimate, not a cryptographic measurement.

## 5. API example
Request `POST /api/analyze-password` with `{"password":"abcd"}`. Response contains `score`, `strength`, `checks`, `reasons`, `suggestions`, `length`, `estimated_guesses_log10`, `disclaimer`. Bad input returns 422 with a generic message.

## 6. Security and privacy
No DB, no logging of bodies, no localStorage/sessionStorage, no third-party calls, generic errors, local CORS only, local development only.

## 7. Twenty technical questions
1. **Why FastAPI?** Fast to write, automatic validation with Pydantic, and automatic docs at `/docs`.
2. **What does Pydantic do here?** Checks the request body type, length and extra fields before my code runs.
3. **What is CORS?** A browser rule that blocks a page from calling another origin unless the server allows it. I allow only localhost:5173.
4. **Why POST and not GET?** GET puts data in the URL, which can be logged. POST puts it in the body.
5. **What is zxcvbn?** A password strength estimator from Dropbox that detects dictionary words, patterns, dates and l33t substitutions.
6. **Why not only count character types?** `Password1!` passes all rules but is very guessable.
7. **How do you detect repeats?** Regex `(.)\1{2,}`: any character followed by itself twice or more.
8. **How do you detect sequences?** I compare character codes of neighbours (differences of +1 or -1) for 4+ in a row, and check keyboard rows like `qwertyuiop`.
9. **What does a "cap" do?** It lowers the final score when a weakness exists, so a weak pattern can't be hidden by a long length.
10. **Why a 128 character limit?** To prevent very large inputs from slowing the server (basic denial-of-service protection).
11. **How do you avoid leaking the password in errors?** A custom handler replaces FastAPI's default 422 (which echoes input) with a fixed message.
12. **Do you log passwords?** No. The 500 handler logs only the exception type.
13. **Why is the password in React state only?** Browser storage persists after the page closes; state disappears.
14. **What does Reset do?** Aborts any pending request and clears password, result and errors.
15. **Why use AbortController?** To ignore an old response if the user resets or resubmits.
16. **What is a pure function?** One with no side effects; `analyze_password` only returns a value and stores nothing.
17. **What do your tests cover?** Empty, short, lowercase, mixed, symbols, passphrases, common passwords, sequences, repeats, spaces, Unicode, invalid API requests, CORS.
18. **What is TestClient?** FastAPI's tool to call the API inside tests without starting a server.
19. **Why Vite?** Fast dev server and build tool, the current standard for React projects.
20. **Is a score of 100 "unbreakable"?** No. It means the estimate is high under known attack patterns.

## 8. Limitations and future work
1. **What are the main limitations?** Heuristic score; no breach check; small common list; local use only.
2. **Is sending the password to a backend safe?** Only because the backend is on localhost. In production, do analysis in the browser.
3. **How would you check for breaches privately?** Use the k-anonymity range API (send only the first 5 hash characters) or an offline hash list.
4. **How would you deploy it?** HTTPS, rate limiting, strict CORS, no body logging, containerization, security review.
5. **What would you add next?** Client-side analysis, passphrase generator, more tests, accessibility audit.

## 9. Demo script (3 minutes)
1. Show the two terminals: backend (uvicorn) and frontend (npm run dev). Explain each.
2. Open the page. Point out the empty field, Show/Hide and Clear.
3. Enter `password` → Very Weak; show "common password" reason.
4. Enter `Password1!` → still Weak, even though it has upper, lower, number and symbol.
5. Enter `1234abcd` → sequence warning.
6. Enter a long passphrase of random words → Strong/Very Strong.
7. Click Reset → field and result clear. Stop the backend and click Analyze to show the error state.
8. Open `http://127.0.0.1:8000/docs` to show the API; run `pytest -v` and show the results.
