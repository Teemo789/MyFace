"""Lightweight JSON-based storage for user records."""

import json
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = Path(__file__).resolve().parents[1] / "db.json"


def load_db() -> Dict:
    """Load database content or initialize an empty structure."""
    if not DB_PATH.exists():
        return {"users": []}
    try:
        with DB_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Corrupted JSON; reset to a safe empty structure
        return {"users": []}


def save_db(data: Dict) -> None:
    """Persist database content to disk."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def find_user_by_email(email: str, data: Optional[Dict] = None) -> Optional[Dict]:
    """Return a user dict by email if present."""
    database = data or load_db()
    for user in database.get("users", []):
        if user.get("email") == email:
            return user
    return None


def add_user(user: Dict) -> None:
    """Append a new user to the database and save."""
    data = load_db()
    data.setdefault("users", []).append(user)
    save_db(data)


def update_user(user: Dict) -> None:
    """Replace an existing user entry with the same email."""
    data = load_db()
    updated_users: List[Dict] = []
    for entry in data.get("users", []):
        if entry.get("email") == user.get("email"):
            updated_users.append(user)
        else:
            updated_users.append(entry)
    data["users"] = updated_users
    save_db(data)
