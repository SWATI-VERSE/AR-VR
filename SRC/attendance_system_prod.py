import cv2
import face_recognition
import pickle
import os
import csv
import random
import dlib
import numpy as np
import pyttsx3
import winsound

from datetime import datetime
from scipy.spatial import distance as dist

# PATHS
ENCODINGS_PATH = os.path.join("ENCODINGS", "encodings.pickle")
ATTENDANCE_DIR = "ATTENDANCE"
ATTENDANCE_FILE = os.path.join(ATTENDANCE_DIR, "attendance.csv")
LANDMARK_PATH = os.path.join(os.path.dirname(__file__), "shape_predictor_68_face_landmarks.dat")

# BLINK SETTINGS
EAR_THRESHOLD = 0.30
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


def get_name_for_rect(rect, boxes, names):
    """
    Map a dlib rect (full-size coords) to the nearest face_recognition box (small image),
    then return the corresponding name.
    """
    rx = (rect.left() + rect.right()) // 2
    ry = (rect.top() + rect.bottom()) // 2

    best_name = "Unknown"
    min_dist = 1e9

    for (top, right, bottom, left), name in zip(boxes, names):
        # convert small box -> full-size
        t, r, b, l = top * 4, right * 4, bottom * 4, left * 4

        cx = (l + r) // 2
        cy = (t + b) // 2

        d = (cx - rx) ** 2 + (cy - ry) ** 2
        if d < min_dist:
            min_dist = d
            best_name = name

    return best_name

def main():

    engine = pyttsx3.init()
    engine.setProperty('rate', 150)   # slower = clearer
    engine.setProperty('volume', 1.0) # max volume

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)   # try 1[FOR FEMALE] or 0[FOR MALE]


    status_memory = {}

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

    ear_values = {}

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

        # BLINK DETECTION (FIXED & SAFE)
        for rect in faces_dlib:

            name = get_name_for_rect(rect, boxes, names)

            if name == "Unknown":
                continue

            shape = predictor(gray, rect)
            coords = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])

            left_eye = coords[36:42]
            right_eye = coords[42:48]

            #  CALCULATE EAR FIRST
            EAR = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

            #  NOW STORE IT
            ear_values[name] = EAR

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

            # if name != "Unknown":
            #    print(f"EAR for {name}: {EAR}")


        # MAIN LOOP
        for (top, right, bottom, left), name in zip(boxes, names):

            status = "Initializing..."

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            face_center_x = (left + right) // 2

            if name != "Unknown":

                if name not in status_memory:
                    status_memory[name] = {
                        "blink": False,
                        "move": False,
                        "time": False,
                        "verified": False
                    }


                if name not in first_position:
                    first_position[name] = face_center_x

                if challenge == "TURN_LEFT":
                    if face_center_x < first_position[name] - 20:
                        if name not in movement_verified:
                            print(f"[LIVENESS] Movement LEFT for {name}")
                        movement_verified.add(name)
                else:
                    if face_center_x > first_position[name] + 20:
                        if name not in movement_verified:
                            print(f"[LIVENESS] Movement RIGHT for {name}")
                        movement_verified.add(name)

                now = datetime.now()

                if name not in first_seen_time:
                    first_seen_time[name] = now
                    elapsed = 0
                else:
                    elapsed = (now - first_seen_time[name]).total_seconds()

                if name in blink_verified:
                    status_memory[name]["blink"] = True

                if name in movement_verified:
                    status_memory[name]["move"] = True

                if elapsed >= required_duration:
                    status_memory[name]["time"] = True


                blink_ok = status_memory[name]["blink"]
                move_ok = status_memory[name]["move"]
                time_ok = status_memory[name]["time"]

                blink_symbol = '✔' if blink_ok else '✘'
                move_symbol = '✔' if move_ok else '✘'
                time_symbol = '✔' if time_ok else '✘'


                if blink_ok and move_ok and time_ok:
                    status_memory[name]["verified"] = True

                    if name not in marked_names:
                        mark_attendance(name, marked_names)

                        #  Sound first
                        winsound.Beep(1000, 200)

                        #  Then speak
                        engine.say(f"Hello {name}. Identity verified. Your attendance has been successfully marked.")
                        engine.runAndWait()


                # ALWAYS SET STATUS AFTER THAT
                if status_memory[name]["verified"]:
                    status = "LIVE VERIFIED "

                else:
                    status = f"Blink {blink_symbol} | Move {move_symbol} | Time {time_symbol}"


            else:
                status = "Unknown"

            if name == "Unknown":
                color = (0, 0, 255)
            elif "VERIFIED" in status:
                color = (0, 220, 0) #green box
            else:
                color = (0, 165, 255) #orange for processing


            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            text = f"{name} | {status}"

            # Get text size
            (text_width, text_height), _ = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )

            # Draw background rectangle (DARK GRAY)
            padding = 6

            cv2.rectangle(frame,
                        (left - padding, top - 35),
                        (left + text_width + padding, top),
                        (30, 30, 30),
                        -1)


            cv2.putText(frame, text,
                        (left + 4, top - 8),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65, (255, 255, 255), 2,
                        cv2.LINE_AA)

        # ===== ACTION BOX =====
        action_text = f"Action: {challenge}"

        (action_w, action_h), _ = cv2.getTextSize(
            action_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2
        )

        # Draw background box
        cv2.rectangle(frame,
                    (5, 5),
                    (5 + action_w + 20, 5 + action_h + 20),
                    (30, 30, 30),
                    -1)

        # Draw text
        cv2.putText(frame,
                    action_text,
                    (15, 5 + action_h + 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 200, 255),  # orange-yellow
                    2)

        # ===== EAR BOX (BELOW WITH GAP) =====
        ear_text = "EAR: --"

        for name in names:
            if name in ear_values:
                ear_text = f"EAR: {ear_values[name]:.2f}"
                break

        # Dynamic color
        ear_color = (0, 255, 0) if ear_values.get(name, 1) > EAR_THRESHOLD else (0, 0, 255)

        (ear_w, ear_h), _ = cv2.getTextSize(
            ear_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2
        )

        # Position BELOW action with GAP
        y_offset = 5 + action_h + 30

        # Draw EAR background
        cv2.rectangle(frame,
                    (5, y_offset),
                    (5 + ear_w + 20, y_offset + ear_h + 20),
                    (30, 30, 30),
                    -1)

        # Draw EAR text
        cv2.putText(frame,
                    ear_text,
                    (15, y_offset + ear_h + 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    ear_color,
                    2)

        cv2.imshow("Secure Attendance", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == ord("Q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Done.")


if __name__ == "__main__":
    main()