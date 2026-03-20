import cv2
import os

# Path to dataset
dataset_path = "DATASET"

def augment_image(image):
    augmented_images = []

    # 1. Original
    augmented_images.append(image)

    # 2. Flip
    flip = cv2.flip(image, 1)
    augmented_images.append(flip)

    # 3. Brightness Increase
    bright = cv2.convertScaleAbs(image, alpha=1.3, beta=30)
    augmented_images.append(bright)

    # 4. Rotation
    h, w = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((w/2, h/2), 15, 1)
    rotated = cv2.warpAffine(image, matrix, (w, h))
    augmented_images.append(rotated)

    return augmented_images


for person in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, person)

    for img_name in os.listdir(person_path):
        img_path = os.path.join(person_path, img_name)
        image = cv2.imread(img_path)

        augmented = augment_image(image)

        count = 0
        for aug_img in augmented:
            new_name = f"{img_name.split('.')[0]}_aug_{count}.jpg"
            new_path = os.path.join(person_path, new_name)
            cv2.imwrite(new_path, aug_img)
            count += 1

print("✅ Data Augmentation Complete!")