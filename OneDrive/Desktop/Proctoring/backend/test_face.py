# import cv2
# from face_detection import FaceDetector
# from event_logic import ProctorEventLogic

# detector = FaceDetector()
# logic = ProctorEventLogic()

# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     face_count, conf = detector.detect(frame)
#     events = logic.process(face_count)

#     y = 40
#     for event in events:
#         cv2.putText(frame, event, (20, y),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
#         y += 40

#     cv2.putText(frame, f"Faces: {face_count}", (20, 200),
#                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

#     cv2.imshow("Proctoring Test", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()

import cv2
from backend.detectors.face_detector import FaceDetector
from backend.logic.event_logic import ProctorEventLogic
from backend.db.db import ProctorDB

detector = FaceDetector()
logic = ProctorEventLogic()
db = ProctorDB()

cap = cv2.VideoCapture(0)
frame_no = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_no += 1
    face_count, conf = detector.detect(frame)
    avg_conf = round(sum(conf)/len(conf), 2) if conf else 0.0

    db.insert_face_confidence(frame_no, face_count, avg_conf)

    events = logic.process(face_count)
    for event, start, end in events:
        db.insert_event(event, start, end)

    cv2.imshow("Proctoring DB Test", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
db.close()
cv2.destroyAllWindows()
