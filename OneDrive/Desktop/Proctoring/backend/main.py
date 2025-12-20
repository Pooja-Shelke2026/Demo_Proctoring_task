import cv2
import time
import sounddevice as sd

from detectors.face_detector import FaceDetector
from detectors.gaze_detector import GazeDetector
from detectors.phone_detector import PhoneDetector
from detectors.audio_detector import AudioDetector

from logic.event_logic import ProctorEventLogic

from db.db import (
    create_session,
    insert_frame,
    insert_event,
    insert_analysis_log
)

from config.config import DB_CONFIG


# ---------------- EVENT SAFETY ----------------
ALLOWED_EVENTS = {
    "NO_FACE",
    "MULTIPLE_PERSON",
    "PHONE",
    "AUDIO_SPIKE"
}

def safe_insert_event(session_id, event_type, start_ms, end_ms, severity):
    if event_type not in ALLOWED_EVENTS:
        if "AUDIO" in event_type:
            event_type = "AUDIO_SPIKE"
        else:
            return
    insert_event(session_id, event_type, start_ms, end_ms, severity)


# ---------------- INIT ----------------
USER_ID = 1
EXAM_ID = 101

face_detector = FaceDetector()
gaze_detector = GazeDetector()
phone_detector = PhoneDetector()
audio_detector = AudioDetector()

logic = ProctorEventLogic()

session_id = create_session(USER_ID, EXAM_ID)
cap = cv2.VideoCapture(0)

audio_stream = sd.InputStream(
    samplerate=audio_detector.sample_rate,
    channels=1,
    dtype="float32",
    blocksize=audio_detector.frame_size
)
audio_stream.start()

start_time = time.time()


# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    timestamp_ms = int((time.time() - start_time) * 1000)

    # ---- Face ----
    face_count, conf = face_detector.detect(frame)
    detection_score = max(conf) if conf else 0.0
    stability_factor = 1.0 if face_count == 1 else 0.0
    face_confidence = round(detection_score * stability_factor, 2)

    # ---- Gaze ----
    gaze_direction = gaze_detector.detect_gaze(frame)

    # ---- Phone ----
    phone_detected, phone_conf = phone_detector.detect_phone(frame)

    # ---- Insert frame ----
    frame_id = insert_frame(
        session_id,
        timestamp_ms,
        face_count,
        detection_score,
        stability_factor,
        face_confidence,
        gaze_direction,
        phone_detected
    )

    # ---- Audio ----
    audio_data, _ = audio_stream.read(audio_detector.frame_size)
    audio_frame = audio_data.flatten()

    audio_flag, audio_type, rms = audio_detector.process_audio(audio_frame)

    if audio_flag:
        safe_insert_event(
            session_id,
            "AUDIO_SPIKE",
            timestamp_ms,
            timestamp_ms,
            severity=2
        )

        insert_analysis_log(
        session_id,
        frame_id,
        "AUDIO",
        f"{audio_type} detected",
        {"rms": rms, "type": audio_type}
)


    # ---- Phone Event ----
    if phone_detected:
        safe_insert_event(
            session_id,
            "PHONE",
            timestamp_ms,
            timestamp_ms,
            severity=3
        )

        insert_analysis_log(
        session_id,
        frame_id,
        "PHONE",
        "Phone detected",
        {"confidence": phone_conf}
)


    # ---- Face-based events ----
    events, _ = logic.process(face_count)

    for event, start, end in events:
        safe_insert_event(
            session_id,
            event,
            int(start * 1000),
            int(end * 1000),
            severity=2
        )

    # ---- Gaze log (frame-level) ----
    insert_analysis_log(
    session_id,
    frame_id,
    "GAZE",
    "Gaze detected",
    {"direction": gaze_direction}
)

    cv2.imshow("Proctoring Prototype", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break


# ---------------- CLEANUP ----------------
audio_stream.stop()
audio_stream.close()

cap.release()
cv2.destroyAllWindows()

audio_data, _ = audio_stream.read(audio_detector.frame_size)
audio_frame = audio_data.flatten()

print("AUDIO SAMPLE (first 5):", audio_frame[:5])
#====------------------Risk score calculation------------------
from logic.risk_engine import RiskEngine
from db.db import get_session_events, insert_risk_score

risk_engine = RiskEngine()

events = get_session_events(session_id)
risk_score = risk_engine.calculate_score(events)
risk_level = risk_engine.map_risk_level(risk_score)

insert_risk_score(session_id, risk_score, risk_level)

print(f"Final Risk Score: {risk_score}, Level: {risk_level}")


