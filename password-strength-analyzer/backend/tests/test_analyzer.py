"""Unit tests for the analyzer. All sample passwords are made-up examples."""
import pytest

from app.analyzer import analyze_password, has_sequence, label_for

ORDER = ["Very Weak", "Weak", "Moderate", "Strong", "Very Strong"]


def rank(result):
    return ORDER.index(result["strength"])


def test_empty_input():
    r = analyze_password("")
    assert r["score"] == 0
    assert r["strength"] == "Very Weak"
    assert not any(r["checks"].values())


def test_very_short_password():
    r = analyze_password("aB3$")
    assert r["strength"] in ("Very Weak", "Weak")
    assert r["score"] <= 25
    assert r["checks"]["length"] is False


def test_only_lowercase():
    r = analyze_password("zebrakitchen")
    assert r["checks"]["lowercase"] is True
    assert r["checks"]["uppercase"] is False
    assert r["checks"]["number"] is False
    assert rank(r) <= 2


def test_upper_and_lower():
    r = analyze_password("PlumTreeRiver")
    assert r["checks"]["uppercase"] and r["checks"]["lowercase"]


def test_numbers_and_special():
    r = analyze_password("kT9#mQ2$vL7!xR")
    assert r["checks"]["number"] and r["checks"]["special_character"]
    assert rank(r) >= 3


def test_long_passphrase_is_strong():
    r = analyze_password("correct violet bicycle staple orbit")
    assert r["checks"]["length"] is True
    assert rank(r) >= 3


def test_common_password_is_very_weak():
    r = analyze_password("password123")
    assert r["strength"] == "Very Weak"
    assert r["checks"]["not_common"] is False


def test_common_password_case_insensitive():
    assert analyze_password("PASSWORD")["strength"] == "Very Weak"


def test_character_rules_alone_do_not_make_it_strong():
    # Has upper, lower, number, special -- but is a predictable pattern.
    r = analyze_password("Password1!")
    assert all(r["checks"][k] for k in ("uppercase", "lowercase", "number", "special_character"))
    assert rank(r) <= 1


@pytest.mark.parametrize("pw", ["12345678", "abcdefgh", "qwertyui", "87654321"])
def test_sequences_detected(pw):
    assert has_sequence(pw) is True
    r = analyze_password(pw)
    assert r["checks"]["no_sequence"] is False
    assert r["score"] <= 35


def test_no_sequence_in_random_text():
    assert has_sequence("kT9mQ2vL") is False


def test_repeated_characters():
    r = analyze_password("aaaaBBBB1111")
    assert r["checks"]["no_repeats"] is False
    assert r["score"] <= 45


def test_spaces_supported():
    r = analyze_password("blue  mango  tiger  lamp")
    assert r["length"] == 24
    assert rank(r) >= 3


def test_unicode_supported():
    r = analyze_password("Ünïcödé-Pässwört-ñandú-42")
    assert r["checks"]["uppercase"] and r["checks"]["lowercase"]
    assert r["score"] > 0


def test_password_not_in_result():
    pw = "UniqueSample-Xyz-98765"
    assert pw not in str(analyze_password(pw))


@pytest.mark.parametrize("score,label", [(0, "Very Weak"), (19, "Very Weak"), (20, "Weak"),
                                          (40, "Moderate"), (60, "Strong"), (80, "Very Strong")])
def test_labels(score, label):
    assert label_for(score) == label
