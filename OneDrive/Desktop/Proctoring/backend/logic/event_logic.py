
import time


class ProctorEventLogic:
    def __init__(self, no_face_threshold=3):
        self.no_face_threshold = no_face_threshold
        self.no_face_start = None
        self.single_face_streak = 0

    def process(self, face_count):
        events = []
        now = time.time()

        # -------- Face stability --------
        if face_count == 1:
            self.single_face_streak += 1
        else:
            self.single_face_streak = 0

        stability_factor = min(self.single_face_streak / 10, 1.0)
        # 10 continuous frames = fully stable

        # -------- NO_FACE logic --------
        if face_count == 0:
            if self.no_face_start is None:
                self.no_face_start = now
            elif now - self.no_face_start >= self.no_face_threshold:
                events.append(("NO_FACE", self.no_face_start, now))
        else:
            self.no_face_start = None

        # -------- MULTIPLE_PERSON --------
        if face_count > 1:
            events.append(("MULTIPLE_PERSON", now, now))

        return events, stability_factor
