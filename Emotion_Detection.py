import cv2
import mediapipe as mp
import math

# Initialize drawing utilities
mp_drawing = mp.solutions.drawing_utils

# Define the indices for facial landmarks
selected_indices = [
    33, 133, 362, 263,  # Eye corners (left & right)
    70, 105, 336, 300,  # Eyebrow (inner & outer points)
    1, 4, 197, 195, 5,  # Nose tip and nostrils
    61, 291, 13, 14,    # Mouth corners and lip centers
    10, 152, 234, 454   # Jawline and cheekbones
]

def calculate_angle(p1, p2, p3):
    """Calculate the angle between three points."""
    angle = math.degrees(math.atan2(p3.y - p2.y, p3.x - p2.x) -
                         math.atan2(p1.y - p2.y, p1.x - p2.x))
    return abs(angle)

def classify_face(landmarks):
    """Classify the emotion based on facial landmarks."""
    if landmarks:
        # Retrieve relevant landmarks
        left_eye_inner = landmarks.landmark[133]
        right_eye_inner = landmarks.landmark[362]
        left_eyebrow_inner = landmarks.landmark[70]
        right_eyebrow_inner = landmarks.landmark[300]
        upper_lip = landmarks.landmark[13]
        lower_lip = landmarks.landmark[14]
        left_mouth_corner = landmarks.landmark[61]
        right_mouth_corner = landmarks.landmark[291]

        # Calculate metrics
        smile_curve = (left_mouth_corner.y + right_mouth_corner.y) / 2 - (upper_lip.y + lower_lip.y) / 2
        mouth_width = abs(left_mouth_corner.x - right_mouth_corner.x)
        mouth_openness = abs(upper_lip.y - lower_lip.y)

        left_eyebrow_eye_angle = calculate_angle(left_eyebrow_inner, left_eye_inner, right_eye_inner)
        right_eyebrow_eye_angle = calculate_angle(right_eyebrow_inner, right_eye_inner, left_eye_inner)

        # Define thresholds for each emotion
        happy_threshold = mouth_width > 0.05 and (smile_curve < 0 and mouth_openness < 0.02)
        fear_threshold = (left_eyebrow_eye_angle > 20 or right_eyebrow_eye_angle > 20) and mouth_openness > 0.03
        distress_threshold = (left_eyebrow_eye_angle > 10 or right_eyebrow_eye_angle > 10) and mouth_openness > 0.02
        neutral_threshold = not (happy_threshold or fear_threshold or distress_threshold)

        # Classification logic
        if happy_threshold:
            return "Happy"
        elif fear_threshold:
            return "Fear"
        elif distress_threshold:
            return "Distress"
        elif neutral_threshold:
            return "Neutral Face"
    return "Face Not Detected"

def process_faces(frame, female_bboxes, male_bboxes):
    """Process detected faces to classify emotions."""
    with mp.solutions.holistic.Holistic(static_image_mode=False, min_detection_confidence=0.7) as holistic:
        for bbox_list, label in zip([female_bboxes, male_bboxes], ["Female", "Male"]):
            for x1, y1, x2, y2 in bbox_list:
                face_region = frame[max(0, y1):min(y2, frame.shape[0]), max(0, x1):min(x2, frame.shape[1])]
                face_region = cv2.resize(face_region, (256, 256), interpolation=cv2.INTER_AREA)
                
                results = holistic.process(cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB))
                
                if results:
                    emotion = classify_face(results)
                    print(f"{label} emotion: {emotion}")
                else:
                    print(f"No landmarks detected for {label} in region ({x1}, {y1}, {x2}, {y2})")
