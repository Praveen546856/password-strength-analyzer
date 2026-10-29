"""Password analysis logic (pure functions: input in, result out, nothing saved).

SCORING (documented, transparent)
---------------------------------
1. Base score (0-100) comes from zxcvbn's guess estimate:
       base = min(100, log10(guesses) / 12 * 100)
   zxcvbn already understands dictionary words, keyboard patterns, dates,
   repeats, sequences and l33t substitutions like "p@ssw0rd".
2. Our own rules then CAP the score (a cap can only lower it):
       empty password               -> 0
       in our common-password list  -> max 5
       shorter than 8 characters    -> max 25
       contains a sequence (abcd, 1234, qwer) -> max 35
       contains a repeat (aaa)      -> max 45
       shorter than 12 characters   -> max 70  (so never "Very Strong")
3. The final score maps to a label:
       0-19 Very Weak | 20-39 Weak | 40-59 Moderate | 60-79 Strong | 80-100 Very Strong

LIMITATION: this is an estimate based on known attack patterns, NOT a
cryptographically exact measurement. It cannot know if a password was leaked.
"""
import math
import re

from zxcvbn import zxcvbn

from .common_passwords import COMMON_PASSWORDS

MIN_RECOMMENDED_LENGTH = 12
MIN_ACCEPTABLE_LENGTH = 8

DISCLAIMER = (
    "This score is a heuristic estimate, not a cryptographic guarantee. "
    "It cannot tell whether your password appeared in a past data breach."
)

# Regex: the same character 3 or more times in a row (aaa, 111, !!!).
REPEAT_RE = re.compile(r"(.)\1{2,}", re.DOTALL)
SPECIAL_RE = re.compile(r"[^\w\s]|_")
DIGIT_RE = re.compile(r"\d")

KEYBOARD_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890")


def label_for(score: int) -> str:
    if score < 20:
        return "Very Weak"
    if score < 40:
        return "Weak"
    if score < 60:
        return "Moderate"
    if score < 80:
        return "Strong"
    return "Very Strong"


def has_sequence(password: str, run: int = 4) -> bool:
    """True if `run` or more characters step up/down by one (abcd, 4321, qwer)."""
    text = password.lower()
    # Straight alphabet / digit runs using character codes.
    count_up = count_down = 1
    for prev, cur in zip(text, text[1:]):
        if cur.isalnum() and prev.isalnum() and ord(cur) - ord(prev) == 1:
            count_up += 1
        else:
            count_up = 1
        if cur.isalnum() and prev.isalnum() and ord(prev) - ord(cur) == 1:
            count_down += 1
        else:
            count_down = 1
        if count_up >= run or count_down >= run:
            return True
    # Keyboard rows, forwards and backwards.
    for row in KEYBOARD_ROWS:
        for chunk in (row, row[::-1]):
            for i in range(len(chunk) - run + 1):
                if chunk[i : i + run] in text:
                    return True
    return False


def is_common(password: str) -> bool:
    return password.lower() in COMMON_PASSWORDS


def analyze_password(password: str) -> dict:
    """Analyze a password and return a result dict. The password is not stored."""
    length = len(password)

    checks = {
        "length": length >= MIN_RECOMMENDED_LENGTH,
        "uppercase": any(c.isupper() for c in password),
        "lowercase": any(c.islower() for c in password),
        "number": bool(DIGIT_RE.search(password)),
        "special_character": bool(SPECIAL_RE.search(password)),
        "not_common": length > 0 and not is_common(password),
        "no_sequence": length > 0 and not has_sequence(password),
        "no_repeats": length > 0 and not REPEAT_RE.search(password),
    }

    if length == 0:
        return {
            "score": 0,
            "strength": "Very Weak",
            "checks": checks,
            "reasons": ["No password was entered."],
            "suggestions": ["Enter a password to analyze it."],
            "length": 0,
            "estimated_guesses_log10": 0.0,
            "disclaimer": DISCLAIMER,
        }

    result = zxcvbn(password)
    guesses = max(float(result["guesses"]), 1.0)
    guesses_log10 = round(math.log10(guesses), 2)
    score = min(100, int(guesses_log10 / 12 * 100))

    reasons: list[str] = []
    suggestions: list[str] = []
    caps: list[int] = []

    if not checks["not_common"]:
        caps.append(5)
        reasons.append("This is one of the most commonly used passwords.")
        suggestions.append("Avoid common passwords; attackers try them first.")
    if length < MIN_ACCEPTABLE_LENGTH:
        caps.append(25)
        reasons.append(f"Only {length} characters long (very short).")
    if not checks["no_sequence"]:
        caps.append(35)
        reasons.append("Contains a predictable sequence such as abcd, 1234 or qwer.")
        suggestions.append("Avoid predictable sequences like 1234, abcd or qwerty.")
    if not checks["no_repeats"]:
        caps.append(45)
        reasons.append("Contains the same character repeated 3 or more times.")
        suggestions.append("Avoid repeating the same character (for example aaa or 111).")
    if length < MIN_RECOMMENDED_LENGTH:
        caps.append(70)
        reasons.append(f"Shorter than {MIN_RECOMMENDED_LENGTH} characters.")
        suggestions.append("Use a longer password or a passphrase of 12+ characters.")

    if caps:
        score = min([score] + caps)
    score = max(0, min(100, score))

    # Use zxcvbn's own feedback (it explains dictionary/pattern weaknesses).
    feedback = result.get("feedback", {})
    if feedback.get("warning"):
        reasons.append(f"Pattern warning: {feedback['warning']}")
    for tip in feedback.get("suggestions", []):
        suggestions.append(tip)

    if not (checks["uppercase"] and checks["lowercase"]):
        suggestions.append("Mix uppercase and lowercase letters.")
    if not checks["number"]:
        suggestions.append("Add numbers.")
    if not checks["special_character"]:
        suggestions.append("Add special characters, or use a long passphrase of random words.")

    strength = label_for(score)
    if not reasons:
        reasons.append(
            f"Estimated at about 10^{guesses_log10} guesses and no weak patterns were found."
        )
    if all(checks.values()) and score < 60:
        reasons.append(
            "It meets every character rule, but is still predictable, so the rating stays lower."
        )

    # General advice is always useful.
    suggestions.extend(
        [
            "Do not reuse this password on other accounts.",
            "Consider a reputable password manager.",
            "Enable multifactor authentication (MFA) where available.",
        ]
    )

    # Remove duplicates but keep order.
    seen = set()
    unique = [s for s in suggestions if not (s in seen or seen.add(s))]

    return {
        "score": score,
        "strength": strength,
        "checks": checks,
        "reasons": reasons,
        "suggestions": unique,
        "length": length,
        "estimated_guesses_log10": guesses_log10,
        "disclaimer": DISCLAIMER,
    }
