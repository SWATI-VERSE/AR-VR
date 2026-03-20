import cv2
import face_recognition
import pickle
import os
import csv
import random
import dlib
import numpy as np
from datetime import datetime
from scipy.spatial import distance as dist

# PATHS
ENCODINGS_PATH = os.path.join("ENCODINGS", "encodings.pickle")
ATTENDANCE_DIR = "ATTENDANCE"
ATTENDANCE_FILE = os.path.join(ATTENDANCE_DIR, "attendance.csv")
LANDMARK_PATH = os.path.join(os.path.dirname(__file__), "shape_predictor_68_face_landmarks.dat")

# BLINK SETTINGS
EAR_THRESHOLD = 0.27
CONSEC_FRAMES = 2

# INIT DLIB
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(LANDMARK_PATH)


def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)


def load_encodings():
    if not os.path.exists(ENCODINGS_PATH):
        print("Run encode_faces.py first.")
        return None

    with open(ENCODINGS_PATH, "rb") as f:
        data = pickle.load(f)

    print(f"[INFO] Loaded {len(data['encodings'])} encodings.")
    return data


def init_attendance_file():
    if not os.path.exists(ATTENDANCE_DIR):
        os.makedirs(ATTENDANCE_DIR)

    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Date", "Time"])


def mark_attendance(name, marked_names):
    if name in marked_names:
        return

    now = datetime.now()

    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            name,
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
        ])

    marked_names.add(name)
    print(f"[ATTENDANCE] {name} at {now}")


def main():
    data = load_encodings()
    if data is None:
        return

    init_attendance_file()

    known_encodings = data["encodings"]
    known_names = data["names"]

    cap = cv2.VideoCapture(0)

    marked_names = set()
    first_seen_time = {}
    blink_counter = {}
    blink_verified = set()

    required_duration = 3

    challenge = random.choice(["TURN_LEFT", "TURN_RIGHT"])
    first_position = {}
    movement_verified = set()

    print("Press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb_small)
        encodings = face_recognition.face_encodings(rgb_small, boxes)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_dlib = detector(gray)

        names = []

        for encoding in encodings:
            distances = face_recognition.face_distance(known_encodings, encoding)
            best_idx = distances.argmin()

            if distances[best_idx] < 0.38:
                name = known_names[best_idx]
            else:
                name = "Unknown"

            names.append(name)

        # BLINK DETECTION (FIXED)
        for rect, name in zip(faces_dlib, names):

            if name == "Unknown":
                continue

            shape = predictor(gray, rect)
            coords = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])

            left_eye = coords[36:42]
            right_eye = coords[42:48]

            EAR = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

            if name not in blink_counter:
                blink_counter[name] = 0

            if name not in blink_verified:
                if EAR < EAR_THRESHOLD:
                    blink_counter[name] += 1
                else:
                    if blink_counter[name] >= CONSEC_FRAMES:
                        blink_verified.add(name)
                        print(f"[LIVENESS] Blink detected for {name}")
                    blink_counter[name] = 0

        # MAIN LOOP
        for (top, right, bottom, left), name in zip(boxes, names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            face_center_x = (left + right) // 2

            if name != "Unknown":

                if name not in first_position:
                    first_position[name] = face_center_x

                if challenge == "TURN_LEFT":
                    if face_center_x < first_position[name] - 20:
                        movement_verified.add(name)
                else:
                    if face_center_x > first_position[name] + 20:
                        movement_verified.add(name)

                now = datetime.now()

                if name not in first_seen_time:
                    first_seen_time[name] = now

                elapsed = (now - first_seen_time[name]).total_seconds()

                if (
                    elapsed >= required_duration
                    and name in movement_verified
                    and name in blink_verified
                ):
                    mark_attendance(name, marked_names)
                    status = "LIVE VERIFIED"
                else:
                    status = "Blink + Move"

            else:
                status = "Unknown"

            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, f"{name} | {status}",
                        (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 2)

        cv2.putText(frame, f"Action: {challenge}",
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 255), 2)

        cv2.imshow("Secure Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Done.")


if __name__ == "__main__":
    main()