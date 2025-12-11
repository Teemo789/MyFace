"""Authenticate a user with password and facial verification."""

from getpass import getpass

import numpy as np

from utils.database import find_user_by_email, load_db
from utils.face_capture import compare_face, encode_face_from_frame, capture_pose_image, PoseNotDetectedError
from utils.hashing import verify_password


def capture_login_face() -> np.ndarray:
    """Capture a straightforward face pose for login."""
    print("\nVeuillez regarder la caméra pour la vérification du visage (pose FACE).")
    frame = capture_pose_image("face")
    return encode_face_from_frame(frame)


def main() -> None:
    """Interactive login routine."""
    email = input("Email : ").strip().lower()
    password = getpass("Mot de passe : ")

    database = load_db()
    user = find_user_by_email(email, database)
    if not user:
        print("Utilisateur introuvable.")
        return

    if not verify_password(password, user.get("password", "")):
        print("Mot de passe incorrect.")
        return

    stored_encodings = []
    faces = user.get("faces", {})
    for pose_values in faces.values():
        stored_encodings.append(np.array(pose_values))
    known_array = np.array(stored_encodings)

    try:
        captured_encoding = capture_login_face()
    except PoseNotDetectedError as exc:
        print(f"Échec de la capture : {exc}")
        return
    except RuntimeError as exc:
        print(f"Erreur lors de l'encodage du visage : {exc}")
        return

    if compare_face(captured_encoding, known_array):
        print("Authentification réussie !")
    else:
        print("Vérification faciale refusée.")


if __name__ == "__main__":
    main()
