import cv2
import os

name = input("Enter your name: ")

dataset_path = f"DATASET/{name}"

if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)

camera = cv2.VideoCapture(0)

count = 0

while True:
    ret, frame = camera.read()

    if not ret:
        break

    cv2.imshow("Capturing Faces", frame)

    key = cv2.waitKey(1)

    if key == ord('s'):
        img_path = f"{dataset_path}/{count}.jpg"
        cv2.imwrite(img_path, frame)
        print("Image saved:", img_path)
        count += 1

    if key == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
