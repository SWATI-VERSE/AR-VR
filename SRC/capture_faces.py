import cv2
import os
import time

name = input("Enter your name: ")

dataset_path = f"DATASET/{name}"

if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not access the camera.")
    exit()

count = 0
last_message = "Press 'S' to save, 'Q' to quit"
message_time = 0

while True:
    ret, frame = camera.read()
    if not ret:
        break

    # Show the last message at the top-left
    cv2.putText(
        frame,
        last_message,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    cv2.imshow("Capturing Faces", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') or key == ord('S'):
        img_path = f"{dataset_path}/{count}.jpg"
        cv2.imwrite(img_path, frame)
        count += 1
        last_message = f"Saved image {count} to {img_path}"
        message_time = time.time()
        print(last_message)

    if key == ord('q') or key == ord('Q'):
        break

    # After 2 seconds, go back to default instructions
    if message_time and time.time() - message_time > 2:
        last_message = "Press 'S' to save, 'Q' to quit"
        message_time = 0

camera.release()
cv2.destroyAllWindows()
print(f"Done. Total images saved: {count}")
