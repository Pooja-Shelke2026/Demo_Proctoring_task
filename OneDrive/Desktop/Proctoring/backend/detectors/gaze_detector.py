import cv2
import mediapipe as mp
import numpy as np

class GazeDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,  # IMPORTANT for iris
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def detect_gaze(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return "CENTER"

        landmarks = results.multi_face_landmarks[0].landmark

        # ---- Landmark indices (MediaPipe standard) ----
        LEFT_EYE = [33, 133]
        RIGHT_EYE = [362, 263]
        LEFT_IRIS = [468, 469, 470, 471]

        # ---- Convert to pixel coords ----
        def to_pixel(idx):
            return np.array([int(landmarks[idx].x * w),
                             int(landmarks[idx].y * h)])

        left_eye = to_pixel(LEFT_EYE[0])
        right_eye = to_pixel(LEFT_EYE[1])
        iris_points = np.array([to_pixel(i) for i in LEFT_IRIS])

        iris_center = iris_points.mean(axis=0)

        eye_width = np.linalg.norm(right_eye - left_eye)
        horizontal_ratio = (iris_center[0] - left_eye[0]) / eye_width
        vertical_ratio = (iris_center[1] - left_eye[1]) / eye_width

        # ---- Decision logic ----
        if horizontal_ratio < 0.35:
            return "LEFT"
        elif horizontal_ratio > 0.65:
            return "RIGHT"
        elif vertical_ratio > 0.55:
            return "DOWN"
        else:
            return "CENTER"
