"""
Secure password generation with entropy calculation.
"""

import math
import secrets
import string

# --- Password Generation ---
def generate_password(
    length: int,
    use_uppercase: bool = True,
    use_digits: bool = True,
    use_special_chars: bool = True,
) -> str:
    """Generate a cryptographically secure password."""
    if length < 4:
        raise ValueError("Password length must be at least 4 characters.")

    pool = string.ascii_lowercase
    required: list[str] = [secrets.choice(string.ascii_lowercase)]

    if use_uppercase:
        pool += string.ascii_uppercase
        required.append(secrets.choice(string.ascii_uppercase))

    if use_digits:
        pool += string.digits
        required.append(secrets.choice(string.digits))

    if use_special_chars:
        pool += string.punctuation
        required.append(secrets.choice(string.punctuation))

    if len(required) > length:
        raise ValueError("Length too short for the selected character sets.")

    # Fill remaining slots from full pool
    filler = [secrets.choice(pool) for _ in range(length - len(required))]
    password_chars = required + filler

    # Shuffle with secrets-backed randomness
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def calculate_entropy(password: str) -> float:
    """Estimate password entropy in bits."""
    charset_size = 0
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if any(c in string.punctuation for c in password):
        charset_size += 32

    if charset_size == 0:
        return 0.0
    return round(len(password) * math.log2(charset_size), 2)

# --- Strength ---
def strength_label(entropy: float) -> tuple[str, str]:
    """Return strength label and associated color."""
    if entropy < 28:
        return "Very Weak", "#ef4444"
    if entropy < 36:
        return "Weak", "#f97316"
    if entropy < 60:
        return "Fair", "#eab308"
    if entropy < 80:
        return "Strong", "#22c55e"
    return "Very Strong", "#10b981"
