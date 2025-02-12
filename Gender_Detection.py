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
        
        # Validate bounding box
        if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
            print(f"Skipping invalid bounding box {i}: {box}")
            continue
        
        # Extract the person's region
        person_image = frame[y1:y2, x1:x2]

        # Check if the person region is sufficiently large to perform detection
        if person_image.size > 0 and person_image.shape[0] > 10 and person_image.shape[1] > 10:
            label, confidence = classify_gender(person_image)
            print(f"Predicted for person {i}: {label} with confidence {confidence}")
            
            # Update counts based on predicted label
            if label:  # Only consider results above a confidence threshold
                if "male" == label.lower():
                    male_count += 1
                elif "female" == label.lower():
                    female_count += 1
            else:
                print(f"Low confidence for detected person {i}, skipping...")
        else:
            print(f"Invalid or too small region for bounding box {i}, skipping...")

    return {"males": male_count, "females": female_count}
