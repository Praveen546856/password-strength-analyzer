"""FastAPI app. Privacy rules: no database, no logging of request bodies,
no third-party calls, no password in any error message."""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .analyzer import analyze_password
from .schemas import AnalysisResponse, ErrorResponse, PasswordRequest

# Only log generic problems; we never log request bodies.
logger = logging.getLogger("password_analyzer")

app = FastAPI(
    title="Password Strength Analyzer API",
    version="1.0.0",
    description="Local-only API. Passwords are analyzed in memory and never stored.",
)

# CORS: only the local React dev server may call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    # Default FastAPI errors echo the submitted input. We return a generic message.
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request. Send JSON like {\"password\": \"text\"} (max 128 characters)."},
    )


@app.exception_handler(Exception)
async def unexpected_handler(request: Request, exc: Exception):
    # Log only the exception TYPE, never the message/body (could contain the password).
    logger.error("Unexpected error: %s", type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post(
    "/api/analyze-password",
    response_model=AnalysisResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def analyze(payload: PasswordRequest):
    return analyze_password(payload.password)
