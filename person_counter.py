import cv2
from ultralytics import YOLO

class PersonCounter:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def count(self, frame):
        results = self.model(frame, stream=True, conf=0.4, classes=[0]) # classes=[0] тек адамдарды (person) іздейді
        person_count = 0

        for r in results:
            boxes = r.boxes
            for box in boxes:
                person_count += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Жасыл төртбұрыш сызу
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Adam", (x1, int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        return frame, person_count