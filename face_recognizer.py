import cv2
import os
import time
import face_recognition
import numpy as np


class FaceRecognizer:
    def __init__(self, known_faces_dir='known_faces', unknown_dir='unknown_faces'):
        self.known_faces_dir = known_faces_dir
        self.unknown_dir = unknown_dir

        os.makedirs(self.unknown_dir, exist_ok=True)

        self.known_face_encodings = []
        self.known_face_names = []

        self.last_unknown_save_time = 0
        self.save_cooldown = 5  # секунд
        self.process_every_n_frames = 2
        self.frame_count = 0

        self.load_known_faces()

    def load_known_faces(self):
        if not os.path.exists(self.known_faces_dir):
            print(f"⚠️ {self.known_faces_dir} папкасы табылмады.")
            return

        total_loaded = 0

        for person_name in os.listdir(self.known_faces_dir):
            person_path = os.path.join(self.known_faces_dir, person_name)

            if not os.path.isdir(person_path):
                continue

            for image_name in os.listdir(person_path):
                image_path = os.path.join(person_path, image_name)

                try:
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)

                    if len(encodings) > 0:
                        self.known_face_encodings.append(encodings[0])
                        self.known_face_names.append(person_name)
                        total_loaded += 1
                    else:
                        print(f"⚠️ Бет табылмады: {image_path}")

                except Exception as e:
                    print(f"❌ Қате: {image_path} -> {e}")

        print(f"✅ База жүктелді: {total_loaded} бет")
        print("📌 Танитын адамдар:", list(set(self.known_face_names)))

    def save_unknown_face(self, frame, top, right, bottom, left):
        current_time = time.time()

        if current_time - self.last_unknown_save_time < self.save_cooldown:
            return

        self.last_unknown_save_time = current_time

        face_crop = frame[top:bottom, left:right]
        if face_crop.size == 0:
            return

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.unknown_dir, f"unknown_{timestamp}.jpg")
        cv2.imwrite(filename, face_crop)
        print(f"📸 Бейтаныс адам сақталды: {filename}")

    def recognize(self, frame):
        self.frame_count += 1
        unknown_found = False

        # Кей кадрларды өткізіп өңдеу — лагты азайтады
        if self.frame_count % self.process_every_n_frames != 0:
            return frame, unknown_found

        # OpenCV BGR -> RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Кішірейту — жылдамдық үшін
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)

        face_locations = face_recognition.face_locations(small_frame, model="hog")
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            name = "Unknown"
            color = (0, 0, 255)

            if len(self.known_face_encodings) > 0:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=0.5
                )

                face_distances = face_recognition.face_distance(
                    self.known_face_encodings,
                    face_encoding
                )

                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    color = (0, 255, 0)
                else:
                    unknown_found = True
            else:
                unknown_found = True

            # Координаталарды бастапқы frame өлшеміне қайтару
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            if name == "Unknown":
                self.save_unknown_face(frame, top, right, bottom, left)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(
                frame,
                name,
                (left + 6, bottom - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        return frame, unknown_found