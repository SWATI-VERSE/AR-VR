import os
import cv2
import face_recognition
import pickle

DATASET_DIR = "DATASET"
ENCODINGS_PATH = os.path.join("ENCODINGS", "encodings.pickle")

def main():
    if not os.path.exists("ENCODINGS"):
        os.makedirs("ENCODINGS")

    known_encodings = []
    known_names = []

    for person_name in os.listdir(DATASET_DIR):
        person_dir = os.path.join(DATASET_DIR, person_name)
        if not os.path.isdir(person_dir):
            continue

        print(f"[INFO] Processing images for: {person_name}")

        for file_name in os.listdir(person_dir):
            if not file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            image_path = os.path.join(person_dir, file_name)
            print(f"  [INFO] Encoding {image_path}")

            image = cv2.imread(image_path)
            if image is None:
                print("   [WARN] Could not read image, skipping.")
                continue

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)

            for encoding in encodings:
                known_encodings.append(encoding)
                known_names.append(person_name)

    data = {"encodings": known_encodings, "names": known_names}

    with open(ENCODINGS_PATH, "wb") as f:
        pickle.dump(data, f)

    print(f"[INFO] Saved encodings to {ENCODINGS_PATH}")
    print(f"[INFO] Total faces encoded: {len(known_encodings)}")

if __name__ == "__main__":
    main()
