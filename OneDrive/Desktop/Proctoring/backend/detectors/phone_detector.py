from ultralytics import YOLO

class PhoneDetector:
    def __init__(self, conf_threshold=0.5):
        self.model = YOLO("yolov8n.pt")  # lightweight, good for prototype
        self.conf_threshold = conf_threshold

    def detect_phone(self, frame):
        results = self.model(frame, verbose=False)

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                # COCO class id for cellphone = 67
                if cls_id == 67 and conf >= self.conf_threshold:
                    return True, conf

        return False, 0.0
