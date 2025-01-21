import cv2
import time
import mediapipe as mp
from Person_Detection import detect_person
from Gender_Detection import classify_gender,detect_genders_in_frame
from Centroid_Tracker import CentroidTracker
from SOS_Condition import is_female_surrounded
from Pose_Detection import detect_action
from Telebot_Alert import send_telegram_alert
from Emotion_Detection import classify_face, draw_selected_landmarks  # Import the functions


webcam = cv2.VideoCapture(0)
tracker = CentroidTracker()

mp_holistic = mp.solutions.holistic.Holistic(static_image_mode=False, min_detection_confidence=0.5)
if not webcam.isOpened():
    print("Could not open video")
    exit()

try:
    skip_frame = 2
    frame_count = -1

    while True:
        status, frame = webcam.read()
        if not status:
            print("Failed to read frame from video")
            break

        frame_count += 1
        if frame_count % skip_frame != 0:
            continue

        # Detect persons in the frame
        person_boxes = detect_person(frame)
        n = len(person_boxes)  # stores the number of persons

        # Use detect_genders_in_frame to classify genders
        gender_counts = detect_genders_in_frame(frame, person_boxes)
        male_count = gender_counts["males"]
        female_count = gender_counts["females"]

        print(f"Number of males: {male_count}, Number of females: {female_count}, Total persons: {n}")

        # Display the counts of males, females, and persons for the current frame
        count_text = f'Males: {male_count}  Females: {female_count}  Total Persons: {n}'
        cv2.putText(frame, count_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Alert condition: Female detected alone at night
        if female_count == 1 and male_count == 0:
            send_telegram_alert(frame, "Female detected alone at night!")
            print("Alert sent: Female detected alone at night.")

        # Alert condition: Female surrounded by males
        if female_count > 0 and n > 0:
            # Assuming `is_female_surrounded` logic is implemented correctly
            female_bbox = [frame[y1:y2, x1:x2] for x1, y1, x2, y2 in person_boxes if "female" in classify_gender(frame[y1:y2, x1:x2])[0].lower()]
            male_bboxes = [frame[y1:y2, x1:x2] for x1, y1, x2, y2 in person_boxes if "male" in classify_gender(frame[y1:y2, x1:x2])[0].lower()]
            if is_female_surrounded(female_bbox, male_bboxes):
                send_telegram_alert(frame, "Female surrounded by men, potential danger detected!")
                print("Alert sent: Female surrounded by men.")

        # Annotate the frame with bounding boxes and labels
        for i, box in enumerate(person_boxes):
            x1, y1, x2, y2 = map(int, box)
            label = f"Person {i + 1}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Display the annotated frame
        cv2.imshow("Webcam/Video Feed", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Release resources
    webcam.release()
    cv2.destroyAllWindows()
