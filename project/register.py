"""Register a new user with facial pose samples."""

from getpass import getpass
from typing import Dict

from utils.database import add_user, find_user_by_email, load_db
from utils.face_capture import PoseNotDetectedError, capture_pose_encoding
from utils.hashing import hash_password

POSES = ["face", "left", "right", "up", "down"]


def collect_user_info() -> Dict:
    """Prompt for base user information."""
    first_name = input("Prénom : ").strip()
    last_name = input("Nom : ").strip()
    email = input("Email : ").strip().lower()
    password = getpass("Mot de passe : ")

    if not all([first_name, last_name, email, password]):
        raise ValueError("Tous les champs sont obligatoires.")
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
    }


def capture_all_poses() -> Dict[str, list]:
    """Capture required head poses and return JSON-serializable encodings."""
    encodings: Dict[str, list] = {}
    for pose in POSES:
        print(f"\nVeuillez positionner votre tête pour la pose : {pose.upper()}")
        encoding = capture_pose_encoding(pose)
        encodings[pose] = encoding.tolist()
    return encodings


def main() -> None:
    """Interactive registration entry point."""
    try:
        info = collect_user_info()
    except ValueError as exc:
        print(f"Entrée invalide : {exc}")
        return
    database = load_db()

    if find_user_by_email(info["email"], database):
        print("Un utilisateur avec cet email existe déjà.")
        return

    hashed_password = hash_password(info["password"])

    try:
        pose_data = capture_all_poses()
    except PoseNotDetectedError as exc:
        print(f"Échec de la capture : {exc}")
        return
    except RuntimeError as exc:
        print(f"Erreur lors de l'encodage du visage : {exc}")
        return

    user_record = {
        "first_name": info["first_name"],
        "last_name": info["last_name"],
        "email": info["email"],
        "password": hashed_password,
        "faces": pose_data,
    }

    add_user(user_record)
    print("Inscription réussie !")


if __name__ == "__main__":
    main()
