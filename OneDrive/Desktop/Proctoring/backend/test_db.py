from backend.db.db import create_session, insert_frame, insert_event, insert_analysis_log

# 1. Create session
session_id = create_session(user_id=1, exam_id=101)
print("Session created:", session_id)

# 2. Insert frame data
frame_id = insert_frame(
    session_id=session_id,
    timestamp_ms=1000,
    face_count=1,
    detection_score=0.95,
    stability_factor=0.9,
    face_confidence=0.855
)
print("Frame inserted:", frame_id)

# 3. Insert violation event
insert_event(
    session_id=session_id,
    event_type="NO_FACE",
    start_time_ms=2000,
    end_time_ms=5000,
    severity=2
)
print("Event inserted")

# 4. Insert analysis log
insert_analysis_log(
    session_id=session_id,
    frame_id=frame_id,
    analysis_type="FACE",
    message="Test log: face detected normally"
)
print("Analysis log inserted")
