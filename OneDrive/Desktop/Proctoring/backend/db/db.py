import mysql.connector
from mysql.connector import Error
from datetime import datetime

#from backend.config.config import DB_CONFIG
from config.config import DB_CONFIG



def get_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )


# ---------------- Session ----------------

def create_session(user_id, exam_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO sts_proctor_sessions (user_id, exam_id, start_time)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user_id, exam_id, datetime.now()))
        conn.commit()
        session_id = cursor.lastrowid
        return session_id
    finally:
        cursor.close()
        conn.close()


# ---------------- Frames ----------------

def insert_frame(
    session_id,
    timestamp_ms,
    face_count,
    detection_score,
    stability_factor,
    face_confidence,
    gaze_direction=None,
    phone_detected=False
):

    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO sts_proctor_frames
        (session_id, timestamp_ms, face_count, detection_score,
        stability_factor, face_confidence, gaze_direction, phone_detected)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(query, (
            session_id,
            timestamp_ms,
            face_count,
            detection_score,
            stability_factor,
            face_confidence,
            gaze_direction,
            phone_detected
        ))

        conn.commit()
        frame_id = cursor.lastrowid
        return frame_id
    finally:
        cursor.close()
        conn.close()


# ---------------- Events ----------------

def insert_event(
    session_id,
    event_type,
    start_time_ms,
    end_time_ms=None,
    severity=1
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO sts_proctor_events
            (session_id, event_type, start_time_ms, end_time_ms, severity)
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            session_id,
            event_type,
            start_time_ms,
            end_time_ms,
            severity
        ))

        conn.commit()
        event_id = cursor.lastrowid
        return event_id
    finally:
        cursor.close()
        conn.close()
#---------------------Risk Scores------------------
def get_session_events(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT event_type, severity
        FROM sts_proctor_events
        WHERE session_id = %s
    """

    cursor.execute(query, (session_id,))
    events = cursor.fetchall()

    cursor.close()
    conn.close()
    return events

def insert_risk_score(session_id, risk_score, risk_level):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO sts_proctor_scores
        (session_id, risk_score, risk_level)
        VALUES (%s, %s, %s)
    """

    cursor.execute(query, (session_id, risk_score, risk_level))
    conn.commit()
    cursor.close()
    conn.close()

# ---------------- Analysis Logs ----------------

import json
import numpy as np

def insert_analysis_log(
    session_id,
    frame_id,
    analysis_type,
    message,
    raw_output=None
):
    conn = get_connection()
    cursor = conn.cursor()

    # ---- FIX: convert numpy types to python types ----
    if raw_output is not None:
        if isinstance(raw_output, dict):
            raw_output = {
                k: (float(v) if isinstance(v, np.generic) else v)
                for k, v in raw_output.items()
            }
        elif isinstance(raw_output, np.generic):
            raw_output = float(raw_output)

        raw_output = json.dumps(raw_output)

    query = """
        INSERT INTO sts_proctor_analysis_logs
        (session_id, frame_id, analysis_type, message, raw_output)
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        session_id,
        frame_id,
        analysis_type,
        message,
        raw_output
    ))

    conn.commit()
    cursor.close()
    conn.close()
