import cv2

camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()

    if not ret:
        break

    cv2.imshow("Camera Test", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q') or key == ord('Q'):
            print("Closing camera...")
            break

camera.release()
cv2.destroyAllWindows()
