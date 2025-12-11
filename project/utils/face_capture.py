"""Face capture and pose evaluation utilities using OpenCV, MediaPipe, and face_recognition."""

import math
import time
from typing import Dict, Optional, Tuple

import cv2
import face_recognition
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh


class PoseNotDetectedError(RuntimeError):
    """Raised when a requested pose could not be confirmed."""


def _compute_angles(landmarks: Dict[int, Tuple[float, float, float]]) -> Tuple[float, float]:
    """Return approximate yaw and pitch degrees based on key facial landmarks."""
    left_eye = np.array(landmarks[263])
    right_eye = np.array(landmarks[33])
    nose = np.array(landmarks[1])
    chin = np.array(landmarks[152])

    eye_center = (left_eye + right_eye) / 2
    yaw_radians = math.atan2(nose[0] - eye_center[0], right_eye[0] - left_eye[0])
    yaw_degrees = math.degrees(yaw_radians)

    mid_face = (eye_center + chin) / 2
    pitch_radians = math.atan2(nose[1] - mid_face[1], right_eye[1] - left_eye[1])
    pitch_degrees = math.degrees(pitch_radians)

    return yaw_degrees, pitch_degrees


def _landmarks_to_dict(landmarks) -> Dict[int, Tuple[float, float, float]]:
    points: Dict[int, Tuple[float, float, float]] = {}
    for idx, lm in enumerate(landmarks.landmark):
        points[idx] = (lm.x, lm.y, lm.z)
    return points


def _classify_pose(target_pose: str, yaw: float, pitch: float, yaw_threshold: float, pitch_threshold: float) -> bool:
    target = target_pose.lower()
    if target == "face":
        return abs(yaw) < yaw_threshold and abs(pitch) < pitch_threshold
    if target == "left":
        return yaw > yaw_threshold
    if target == "right":
        return yaw < -yaw_threshold
    if target == "up":
        return pitch < -pitch_threshold
    if target == "down":
        return pitch > pitch_threshold
    return False


def _draw_status(frame, target_pose: str, yaw: float, pitch: float) -> None:
    text = f"Pose: target={target_pose} yaw={yaw:.1f} pitch={pitch:.1f}"
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.imshow("Capture", frame)


def capture_pose_image(target_pose: str, camera_index: int = 0, yaw_threshold: float = 12.0, pitch_threshold: float = 12.0, timeout: int = 40) -> np.ndarray:
    """Capture a frame that matches the requested pose and return the image array."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        cap.release()
        raise RuntimeError("Impossible d'ouvrir la caméra.")

    detector = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
    start_time = time.time()
    matched_frame: Optional[np.ndarray] = None

    try:
        while True:
            if time.time() - start_time > timeout:
                raise PoseNotDetectedError(f"Timeout while waiting for pose '{target_pose}'")

            success, frame = cap.read()
            if not success:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb)

            if results.multi_face_landmarks:
                landmarks_dict = _landmarks_to_dict(results.multi_face_landmarks[0])
                yaw, pitch = _compute_angles(landmarks_dict)

                if _classify_pose(target_pose, yaw, pitch, yaw_threshold, pitch_threshold):
                    matched_frame = frame.copy()
                    _draw_status(frame, target_pose, yaw, pitch)
                    cv2.waitKey(500)
                    break

                _draw_status(frame, target_pose, yaw, pitch)
            else:
                cv2.imshow("Capture", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        detector.close()
        cv2.destroyAllWindows()

    if matched_frame is None:
        raise PoseNotDetectedError(f"Pose '{target_pose}' could not be captured")
    return matched_frame


def encode_face_from_frame(frame: np.ndarray) -> np.ndarray:
    """Encode the first detected face in the given frame."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_frame)
    if not encodings:
        raise RuntimeError("No face encoding detected in captured frame")
    return encodings[0]


def capture_pose_encoding(target_pose: str, camera_index: int = 0) -> np.ndarray:
    """Capture a pose and return the face encoding."""
    frame = capture_pose_image(target_pose, camera_index=camera_index)
    return encode_face_from_frame(frame)


def compare_face(encoding: np.ndarray, known_encodings: np.ndarray, tolerance: float = 0.5) -> bool:
    """Compare a captured face encoding to stored encodings."""
    if known_encodings.size == 0:
        return False
    results = face_recognition.compare_faces(list(known_encodings), encoding, tolerance=tolerance)
    return any(results)
