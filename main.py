import cv2
import threading
import time
import datetime
import os

from weapon_detector import WeaponDetector
from person_counter import PersonCounter
from face_recognizer import FaceRecognizer
from whatsapp_alert import WhatsAppAlert
from state import add_event
from state import add_event


# Телефон камерасы
URL = "http://192.168.43.1:8080/video"


class VideoStream:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()


def save_alert_image(frame):
    os.makedirs("unknown_faces", exist_ok=True)
    filename = f"unknown_faces/alert_{int(time.time())}.jpg"
    cv2.imwrite(filename, frame)
    return filename


def main():
    print("🚀 Модульдер жүктелуде...")

    weapon_model_path = "runs/detect/runs/train/weapon_v1/weights/best.pt"

    weapon_det = WeaponDetector(model_path=weapon_model_path)
    person_cnt = PersonCounter(model_path='yolov8n.pt')
    face_rec = FaceRecognizer(known_faces_dir='known_faces', unknown_dir='unknown_faces')
    alert = WhatsAppAlert()

    print("📌 Модель танитын класстар:", weapon_det.names)

    vs = VideoStream(URL).start()

    print("✅ Камера іске қосылды (q бас → шығу)")

    last_alert_time = 0
    alert_interval = 10  # секунд

    while True:
        frame = vs.read()
        if frame is None:
            continue

        frame = cv2.resize(frame, (640, 480))
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Адам санау
        frame, count = person_cnt.count(frame)

        # Қару detection
        frame, weapon_detected = weapon_det.detect(frame)

        # Адам тану
        frame, unknown_found = face_rec.recognize(frame)

        if weapon_detected:
            cv2.putText(
                frame,
                "QARU ANYQTALDY!",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )

        if unknown_found:
            cv2.putText(
                frame,
                "BEITANYS ADAM!",
                (20, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 165, 255),
                3
            )

        cv2.putText(
            frame,
            f"Adam sany: {count}",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2
        )

        current_time = time.time()

        if (weapon_detected or unknown_found) and (current_time - last_alert_time > alert_interval):
            now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            image_path = save_alert_image(frame)

            # Логқа сақтау
            if weapon_detected:
                add_event("weapon", count=count, image_path=image_path)

            if unknown_found:
                add_event("unknown", count=count, image_path=image_path)

            message = (
                f"🚨 QAUIP ANYQTALDY!\n\n"
                f"🕒 Uaqyty: {now}\n"
                f"📍 Kamera: 1\n"
                f"👥 Adam sany: {count}\n\n"
            )

            if weapon_detected:
                message += "🔫 Qaru anyqtaldy!\n"

            if unknown_found:
                message += "👤 Beitanys adam tabyldy!\n"

            message += "\n⚠️ Juyeni tez arasynda tekseriniz!"

            try:
                alert.send_alert(message)
                print("✅ WhatsApp-qa habar jiberildi")
                print("🖼 Suriet saqtaldy:", image_path)
                last_alert_time = current_time
            except Exception as e:
                print("❌ WhatsApp jiberu qatesi:", e)

        cv2.imshow("AI Security System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vs.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()