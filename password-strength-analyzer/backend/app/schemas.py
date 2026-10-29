"""Pydantic models = the shape of the API request and response."""
from pydantic import BaseModel, ConfigDict, Field

MAX_PASSWORD_LENGTH = 128


class PasswordRequest(BaseModel):
    """Request body. Extra fields are rejected."""

    model_config = ConfigDict(extra="forbid")

    # Empty string is allowed on purpose: the analyzer reports it as Very Weak.
    password: str = Field(..., max_length=MAX_PASSWORD_LENGTH)


class Checks(BaseModel):
    length: bool
    uppercase: bool
    lowercase: bool
    number: bool
    special_character: bool
    not_common: bool
    no_sequence: bool
    no_repeats: bool


class AnalysisResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    strength: str
    checks: Checks
    reasons: list[str]
    suggestions: list[str]
    length: int
    estimated_guesses_log10: float
    disclaimer: str


class ErrorResponse(BaseModel):
    detail: str
