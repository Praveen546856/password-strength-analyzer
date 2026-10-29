"""A small list of very common weak passwords (lowercase).

This is a teaching list, not a full breach database. zxcvbn has its own
much larger dictionary; this list is a second, transparent safety net.
"""

COMMON_PASSWORDS = frozenset(
    {
        "password", "password1", "password123", "passw0rd", "p@ssw0rd",
        "123456", "1234567", "12345678", "123456789", "1234567890",
        "qwerty", "qwerty123", "qwertyuiop", "abc123", "letmein",
        "welcome", "welcome1", "admin", "admin123", "iloveyou",
        "monkey", "dragon", "football", "baseball", "master",
        "login", "princess", "sunshine", "trustno1", "111111",
        "000000", "123123", "654321", "changeme", "default",
    }
)
