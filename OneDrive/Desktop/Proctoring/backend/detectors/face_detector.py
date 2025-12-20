import cv2
import mediapipe as mp

class FaceDetector:
    def __init__(self, min_confidence=0.5):
        self.mp_face = mp.solutions.face_detection
        self.detector = self.mp_face.FaceDetection(
            model_selection=0,
            min_detection_confidence=min_confidence
        )

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb)

        face_count = 0
        confidences = []

        if results.detections:
            face_count = len(results.detections)
            for det in results.detections:
                confidences.append(det.score[0])

        return face_count, confidences
