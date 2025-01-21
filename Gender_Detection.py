import cv2
from transformers import pipeline
from PIL import Image

# Initialize the gender classification pipeline
gender_classifier = pipeline("image-classification", model="rizvandwiki/gender-classification")

def classify_gender(face_image):
    # Check if the face image is too small
    if face_image.shape[0] < 10 or face_image.shape[1] < 10:
        return None, None

    # Convert the face image from BGR to RGB
    rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(rgb_image)

    # Perform gender classification
    results = gender_classifier(images=pil_image)

    # Extract the predicted label and confidence score
    label = results[0]['label']
    confidence = results[0]['score']

    return label, round(confidence,2)

def detect_genders_in_frame(frame, person_boxes):
    """
    Detects genders in the given frame based on person bounding boxes.

    Args:
        frame: The input video frame (numpy array).
        person_boxes: List of bounding boxes for detected persons in the frame, 
                      where each box is represented as [x1, y1, x2, y2].

    Returns:
        dict: A dictionary with total counts of males and females detected.
              Example: {"males": 3, "females": 2}
    """
    male_count = 0
    female_count = 0

    for i, box in enumerate(person_boxes):
        x1, y1, x2, y2 = map(int, box)  # Ensure bounding box values are integers
        person_image = frame[y1:y2, x1:x2]

        # Check if the person region is sufficiently large to perform detection
        if person_image.size > 0:
            label, confidence = classify_gender(person_image)
            if label and confidence >= 0.5:  # Use a confidence threshold
                if "male" in label.lower():
                    male_count += 1
                elif "female" in label.lower():
                    female_count += 1
            else:
                print(f"Low confidence for detected person {i}, skipping...")
        else:
            print(f"Invalid person bounding box {i}, skipping...")

    return {"males": male_count, "females": female_count}
