import cv2
import face_recognition
import pickle
import os
import csv
from datetime import datetime
import numpy as np

ENCODINGS_PATH = os.path.join("ENCODINGS", "encodings.pickle")
ATTENDANCE_DIR = "ATTENDANCE"
ATTENDANCE_FILE = os.path.join(ATTENDANCE_DIR, "attendance.csv")


def load_encodings():
    if not os.path.exists(ENCODINGS_PATH):
        print("Error: Encodings file not found. Run encode_faces.py first.")
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
        print(f"[INFO] Created new attendance file at {ATTENDANCE_FILE}")


def mark_attendance(name, marked_names):
    if name in marked_names:
        return

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, date_str, time_str])

    marked_names.add(name)
    print(f"[ATTENDANCE] {name} at {date_str} {time_str}")


def main():
    data = load_encodings()
    if data is None:
        return

    init_attendance_file()

    known_encodings = data["encodings"]
    known_names = data["names"]

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not access the camera.")
        return

    print("Press 'Q' to quit. 4 Windows: Main | Hist/Thresh | K-means | Watershed")
    marked_names = set()
    first_seen_time = {}
    frame_count = 0

    while True:
        ret, frame = camera.read()
        if not ret:
            break

        frame_count += 1

        # Resize for speed
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces and encode
        boxes = face_recognition.face_locations(rgb_small)
        encodings = face_recognition.face_encodings(rgb_small, boxes)

        names = []

        for encoding in encodings:
            distances = face_recognition.face_distance(known_encodings, encoding)
            best_idx = distances.argmin()
            best_distance = distances[best_idx]

            if best_distance < 0.45:
                name = known_names[best_idx]
            else:
                name = "Unknown"

            names.append(name)

        # Process latest face for demos
        latest_face_roi = None
        latest_name = "Unknown"

        for (top, right, bottom, left), name in zip(boxes, names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            if name != "Unknown":
                if name not in first_seen_time:
                    first_seen_time[name] = datetime.now().strftime("%H:%M:%S")
                mark_attendance(name, marked_names)

            # Store latest face ROI for processing
            h, w = frame.shape[:2]
            y1 = max(0, top)
            y2 = min(h, bottom)
            x1 = max(0, left)
            x2 = min(w, right)

            if y2 > y1 and x2 > x1:
                latest_face_roi = frame[y1:y2, x1:x2]
                latest_name = name

            # AR box and info card
            box_color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)

            label = name
            status = "Present" if name != "Unknown" else "Unknown person"
            time_str = first_seen_time.get(name, "")
            info_text = f"{label} | {status}"
            if time_str:
                info_text += f" @ {time_str}"

            (text_w, text_h), _ = cv2.getTextSize(info_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            card_x1 = left
            card_y1 = max(0, top - text_h - 10)
            card_x2 = left + text_w + 10
            card_y2 = top

            cv2.rectangle(frame, (card_x1, card_y1), (card_x2, card_y2), box_color, cv2.FILLED)
            cv2.putText(frame, info_text, (card_x1 + 5, card_y2 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # ---- IMAGE PROCESSING DEMOS (every 5th frame) ----
        if frame_count % 5 == 0 and latest_face_roi is not None:
            gray_face = cv2.cvtColor(latest_face_roi, cv2.COLOR_BGR2GRAY)
            
            # 1. Histogram + Threshold (PDF concept 1)
            equalised_face = cv2.equalizeHist(gray_face)
            _, binary_face = cv2.threshold(gray_face, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            h_f, w_f = gray_face.shape
            resized_equal = cv2.resize(equalised_face, (w_f, h_f))
            resized_binary = cv2.resize(binary_face, (w_f, h_f))
            
            gray_bgr = cv2.cvtColor(gray_face, cv2.COLOR_GRAY2BGR)
            eq_bgr = cv2.cvtColor(resized_equal, cv2.COLOR_GRAY2BGR)
            bin_bgr = cv2.cvtColor(resized_binary, cv2.COLOR_GRAY2BGR)
            
            stacked_hist = np.hstack([gray_bgr, eq_bgr, bin_bgr])
            cv2.imshow("1. Hist/Thresh (Gray|Eq|Binary)", stacked_hist)

            # 2. K-MEANS SEGMENTATION (PDF concept 2)
            h_k, w_k = gray_face.shape
            data_kmeans = gray_face.reshape((-1, 1)).astype(np.float32)
            criteria_k = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels_k, centers_k = cv2.kmeans(data_kmeans, 4, None, criteria_k, 10, cv2.KMEANS_RANDOM_CENTERS)
            segmented_kmeans = labels_k.reshape((h_k, w_k)).astype(np.uint8) * 64
            segmented_kmeans_bgr = cv2.cvtColor(segmented_kmeans, cv2.COLOR_GRAY2BGR)
            cv2.imshow("2. K-Means (4 clusters)", segmented_kmeans_bgr)

        # Top status text
        cv2.putText(frame, "Press Q to Quit. CV Demos Active", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Smart Attendance System - AR+CV", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == ord("Q"):
            break

    camera.release()
    cv2.destroyAllWindows()
    print("Camera closed. Attendance captured.")


if __name__ == "__main__":
    main()