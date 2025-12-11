"""Utility helpers for password hashing using bcrypt."""

import bcrypt


def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt and return the string digest."""
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a stored bcrypt hash."""
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)
