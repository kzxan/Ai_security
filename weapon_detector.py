import cv2
from ultralytics import YOLO

class WeaponDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.names = self.model.names  # класстар
    
    def detect(self, frame):
        results = self.model(frame, conf=0.6)

        weapon_detected = False

        for r in results:
            boxes = r.boxes
            if boxes is None:
                continue

            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.names[cls_id]

                # 🔴 ТЕК маңызды қаруларды фильтрлеу
                if class_name not in ["Automatic Rifle", "Shotgun", "Knife", "Grenade Launcher"]:
                    continue

                if conf < 0.6:
                    continue

                weapon_detected = True

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                label = f"{class_name}: {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return frame, weapon_detected