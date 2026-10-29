"""API tests using FastAPI's TestClient."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
URL = "/api/analyze-password"


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_valid_request():
    r = client.post(URL, json={"password": "kT9#mQ2$vL7!xR"})
    assert r.status_code == 200
    body = r.json()
    for key in ("score", "strength", "checks", "reasons", "suggestions"):
        assert key in body
    assert 0 <= body["score"] <= 100


def test_empty_password_allowed():
    r = client.post(URL, json={"password": ""})
    assert r.status_code == 200
    assert r.json()["strength"] == "Very Weak"


def test_missing_field():
    assert client.post(URL, json={}).status_code == 422


def test_wrong_type():
    assert client.post(URL, json={"password": 12345}).status_code == 422


def test_extra_field_rejected():
    assert client.post(URL, json={"password": "x", "other": 1}).status_code == 422


def test_too_long_rejected_without_echo():
    secret = "A" * 200
    r = client.post(URL, json={"password": secret})
    assert r.status_code == 422
    assert secret not in r.text


def test_invalid_json():
    r = client.post(URL, content="not json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422
    assert "not json" not in r.text


def test_error_does_not_echo_password():
    r = client.post(URL, json={"password": {"nested": "SampleSecret-Q1"}})
    assert r.status_code == 422
    assert "SampleSecret-Q1" not in r.text


def test_wrong_method():
    assert client.get(URL).status_code == 405


def test_cors_allowed_origin():
    r = client.options(URL, headers={"Origin": "http://localhost:5173",
                                     "Access-Control-Request-Method": "POST"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_blocked_origin():
    r = client.options(URL, headers={"Origin": "http://evil.example",
                                     "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in r.headers
