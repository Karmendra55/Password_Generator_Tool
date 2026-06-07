"""
Core encryption system for PasswordGuard.

Handles:
- user vault creation & authentication
- encryption/decryption using Fernet
- credential storage
- password history management
"""

import base64
import hashlib
import json
import os
import secrets

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

USERS_FILE = "users.json"
_PBKDF2_ITERATIONS = 390_000


# --- Internal Helpers ---

def _vault_path(username: str) -> str:
    """Return safe vault filename for a user."""
    safe = "".join(c for c in username.lower() if c.isalnum() or c in "-_")
    return f"vault_{safe}.db"


def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive encryption key from password + salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_PBKDF2_ITERATIONS,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def _hash_password(password: str, salt: bytes) -> str:
    """Create PBKDF2 hash of master password."""
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITERATIONS).hex()


def _load_vault(username: str) -> dict:
    """Load vault JSON file."""
    path = _vault_path(username)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_vault(username: str, data: dict) -> None:
    """Save vault JSON file."""
    with open(_vault_path(username), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _get_fernet(username: str, master_password: str) -> Fernet:
    """Rebuild Fernet cipher for a user vault."""
    vault = _load_vault(username)
    salt = bytes.fromhex(vault["key_salt"])
    derived = _derive_key(master_password, salt)
    cipher = Fernet(derived)
    fernet_key = cipher.decrypt(vault["sealed_key"].encode())
    return Fernet(fernet_key)


# --- User Management ---
def list_users() -> list[str]:
    """Return all registered usernames."""
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_users(users: list[str]) -> None:
    """Save user list."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def user_exists(username: str) -> bool:
    """Check if username already exists."""
    return username.lower() in [u.lower() for u in list_users()]


# --- Vault lifecycle ---

def vault_exists(username: str = "") -> bool:
    """Return True if at least one user exists (or a specific user's vault)."""
    if username:
        return os.path.exists(_vault_path(username)) and bool(_load_vault(username).get("master_hash"))
    return bool(list_users())


def setup_vault(username: str, master_password: str) -> None:
    """Create a new vault for *username*."""
    fernet_key = Fernet.generate_key()

    salt = secrets.token_bytes(32)
    derived = _derive_key(master_password, salt)
    cipher = Fernet(derived)
    sealed_key = cipher.encrypt(fernet_key).decode()

    hash_salt = secrets.token_bytes(32)
    pw_hash = _hash_password(master_password, hash_salt)

    vault = {
        "username": username,
        "master_hash": pw_hash,
        "master_salt": hash_salt.hex(),
        "key_salt": salt.hex(),
        "sealed_key": sealed_key,
        "credentials": [],
        "history": [],
    }
    _save_vault(username, vault)

    users = list_users()
    if username not in users:
        users.append(username)
        _save_users(users)


def verify_master_password(username: str, master_password: str) -> bool:
    """Verify user password against stored hash."""
    vault = _load_vault(username)
    if not vault.get("master_hash"):
        return False
    salt = bytes.fromhex(vault["master_salt"])
    return _hash_password(master_password, salt) == vault["master_hash"]


def delete_user(username: str, master_password: str) -> bool:
    """Delete a user's vault entirely. Returns True on success."""
    if not verify_master_password(username, master_password):
        return False
    path = _vault_path(username)
    if os.path.exists(path):
        os.remove(path)
    users = [u for u in list_users() if u.lower() != username.lower()]
    _save_users(users)
    return True


# --- History ---

def save_history(entry: str, username: str, master_password: str) -> None:
    """Save encrypted password history entry."""
    vault = _load_vault(username)
    f = _get_fernet(username, master_password)
    encrypted = f.encrypt(entry.encode()).decode()
    vault.setdefault("history", []).append(encrypted)
    _save_vault(username, vault)


def load_history(username: str, master_password: str) -> list[str]:
    """Load decrypted password history."""
    vault = _load_vault(username)
    f = _get_fernet(username, master_password)
    results = []
    for token in vault.get("history", []):
        try:
            results.append(f.decrypt(token.encode()).decode())
        except InvalidToken:
            results.append("[corrupted entry]")
    return results


def delete_history_entry(index: int, username: str, master_password: str) -> None:
    """Delete a single history entry by index."""
    vault = _load_vault(username)
    _get_fernet(username, master_password)  # validate password
    history = vault.get("history", [])
    if 0 <= index < len(history):
        history.pop(index)
    vault["history"] = history
    _save_vault(username, vault)


def clear_history(username: str, master_password: str) -> None:
    """Clear all history entries."""
    vault = _load_vault(username)
    _get_fernet(username, master_password)
    vault["history"] = []
    _save_vault(username, vault)


# --- Crendentials ---

def save_credential(website: str, username_cred: str, password: str,
                    username: str, master_password: str) -> None:
    """Encrypt and store a credential."""
    vault = _load_vault(username)
    f = _get_fernet(username, master_password)
    plaintext = json.dumps({"website": website, "username": username_cred, "password": password})
    encrypted = f.encrypt(plaintext.encode()).decode()
    vault.setdefault("credentials", []).append(encrypted)
    _save_vault(username, vault)


def load_credentials(username: str, master_password: str) -> list[dict]:
    """Load decrypted credentials."""
    vault = _load_vault(username)
    f = _get_fernet(username, master_password)
    results = []
    for token in vault.get("credentials", []):
        try:
            data = json.loads(f.decrypt(token.encode()).decode())
            results.append(data)
        except (InvalidToken, json.JSONDecodeError):
            results.append({"website": "[corrupted]", "username": "", "password": ""})
    return results


def delete_credential(index: int, username: str, master_password: str) -> None:
    """Delete a credential entry."""
    vault = _load_vault(username)
    _get_fernet(username, master_password)
    creds = vault.get("credentials", [])
    if 0 <= index < len(creds):
        creds.pop(index)
    vault["credentials"] = creds
    _save_vault(username, vault)
