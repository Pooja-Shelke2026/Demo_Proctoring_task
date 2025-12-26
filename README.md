# AI Proctoring 

## Overview
This document explains how the AI-based proctoring prototype is implemented, including:
- Which AI models and libraries are used
- What logic is applied
- How confidence scores, violations, and debug information are generated
- How outputs are stored in the database



---

## 1. Face Detection & Face Confidence

### Purpose
- Detect whether a face is present
- Detect multiple faces
- Compute a confidence score for face presence
- Log violations and debug information

---

### Models / Libraries Used

| Task | Library | Reason |
|----|----|----|
| Face detection | MediaPipe Face Detection | Fast, CPU-friendly |
| Face landmarks | MediaPipe Face Mesh | Detailed landmarks |
| Multi-face support | MediaPipe | Built-in |
| Confidence score | Custom logic | Fully explainable |

---

### Logic

1. Run MediaPipe Face Detection on every video frame
2. Count number of detected faces

Rules:
- If face_count == 0 → NO_FACE event
- If face_count > 1 → MULTIPLE_PERSON event

Face confidence is computed as:

```python
face_confidence = detection_score * stability_factor
````

Where:

* detection_score = confidence from MediaPipe
* stability_factor = 1.0 if exactly one face is stable, else 0.0

---

### Data Storage

| Output                    | Database Table                     |
| ------------------------- | ---------------------------------- |
| Face confidence per frame | sts_proctor_frames.face_confidence |
| NO_FACE / MULTIPLE_PERSON | sts_proctor_events                 |
| Debug information         | sts_proctor_analysis_logs (FACE)   |

---

## 2. Head Pose Detection

### Purpose

Detect if the candidate turns their head away from the screen.

---

### Libraries Used

* MediaPipe Face Mesh
* OpenCV
* NumPy

---

### Logic

* Extract facial landmarks
* Estimate head pose using yaw and pitch
* Classify head direction:

  * LEFT
  * RIGHT
  * DOWN
  * CENTER

If head direction is not CENTER → violation is triggered.

---

### Data Storage

| Output                          | Database Table                        |
| ------------------------------- | ------------------------------------- |
| Head pose event                 | sts_proctor_events                    |
| Yaw, pitch, direction, evidence | sts_proctor_analysis_logs (HEAD_POSE) |

---



## 3. Mobile Phone Detection

### Purpose

Detect mobile phone usage during the exam.

---

### Model Used

* YOLOv8 (Ultralytics)

---

### Logic

* Run object detection on each frame
* Detect "cell phone" class
* If confidence exceeds threshold → PHONE violation

---

### Data Storage

| Output                      | Database Table                    |
| --------------------------- | --------------------------------- |
| Phone detected (true/false) | sts_proctor_frames                |
| Phone violation             | sts_proctor_events                |
| Confidence + evidence       | sts_proctor_analysis_logs (PHONE) |

---

## 4. Audio Detection

### Purpose

Detect suspicious sounds or talking during the exam.

---

### Libraries Used

* sounddevice (microphone input)
* NumPy (signal processing)

---

### Logic

* Capture real-time audio samples
* Compute RMS (Root Mean Square) energy

```python
rms = sqrt(mean(audio_frame ** 2))
```

Rules:

* Sudden loud sound → AUDIO_SPIKE
* Continuous sound for multiple frames → CONTINUOUS_AUDIO

This module is rule-based (no speech recognition).

---

### Data Storage

| Output          | Database Table                    |
| --------------- | --------------------------------- |
| Audio violation | sts_proctor_events                |
| RMS values      | sts_proctor_analysis_logs (AUDIO) |

---

## 5. Evidence Capture

### Purpose

Store visual proof when a malicious event occurs.

---

### Logic

* Capture webcam frame at violation time
* Save image to server disk
* Store web-accessible URL in database

Example URL:

```
/evidence/session_37_PHONE_ab12cd34.jpg
```

---

### Data Storage

| Output    | Database Table                       |
| --------- | ------------------------------------ |
| Image URL | sts_proctor_analysis_logs.raw_output |

---

## 6. Risk Score Calculation

### Purpose

Convert raw events into a final exam risk level.

---

### Rule-Based Weights

| Event           | Weight |
| --------------- | ------ |
| PHONE           | +15    |
| MULTIPLE_PERSON | +20    |
| AUDIO_SPIKE     | +5     |
| NO_FACE         | +10    |
| TAB_SWITCH      | +5     |

Final score:

```
risk_score = sum(event_weight × frequency)
```

Risk levels:

* Score < 20 → Low
* 20–50 → Medium
* > 50 → High

---

## 8. Event vs Analysis Logs (Important Design)

* sts_proctor_events → WHAT violation occurred
* sts_proctor_analysis_logs → WHY and HOW it occurred

This separation improves explainability and debugging.

---

## Conclusion

This prototype demonstrates how AI models, rule-based logic, and structured database design can be combined to build an explainable and scalable online exam proctoring backend.


