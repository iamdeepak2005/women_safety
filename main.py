import cv2
import time
import mediapipe as mp
from Person_Detection import detect_person
from Gender_Detection import classify_gender, detect_genders_in_frame
from Centroid_Tracker import CentroidTracker
from SOS_Condition import is_female_surrounded,process_frame
from Telebot_Alert import send_telegram_alert
from Emotion_Detection import classify_face, process_faces  # Import the functions

# Path to the video file
# path1 = r"C:\Users\deepa\Downloads\WhatsApp Video 2025-01-22 at 18.48.29_55a07090.mp4"

# Initialize video capture
# webcam = cv2.VideoCapture(path1)
webcam = cv2.VideoCapture(0)

if not webcam.isOpened():
    print("Could not open video")
    exit()

# Initialize Centroid Tracker
tracker = CentroidTracker()

# Initialize Mediapipe holistic model
mp_holistic = mp.solutions.holistic.Holistic(static_image_mode=False, min_detection_confidence=0.5)

# Frame skipping configuration
skip_frame = 2
frame_count = -1

try:
    while True:
        # Read the next frame
        status, frame = webcam.read()
        if not status:
            print("Failed to read frame from video")
            break

        # Skip frames to process at a lower frame rate
        frame_count += 1
        if frame_count % skip_frame != 0:
            continue

        # Detect persons in the frame
        person_boxes = detect_person(frame)
        n = len(person_boxes)  # Total number of persons detected
        objects = tracker.update(person_boxes)
        print(f"Number of detected persons: {len(person_boxes)}")
        print(f"Number of tracked objects: {len(objects)}")

        for i, (objectID, centroid) in enumerate(objects.items()):
            if objectID < len(person_boxes):
                x1, y1, x2, y2 = map(int, person_boxes[i])  # Ensure bounding box values are integers
                person_image = frame[y1:y2, x1:x2]

                # Check if the person region is sufficiently large to perform detection
                if person_image.size > 0:
                    # Detect and classify facial expression
                    results = mp_holistic.process(cv2.cvtColor(person_image, cv2.COLOR_BGR2RGB))

                    if results.face_landmarks:
                        face_class = classify_face(results.face_landmarks)  # Use the imported classify_face function
                        print("the emotion observed is this",face_class)
                        if face_class=="Distress" or face_class=="Fear":
                            gender_label = classify_gender(person_image)
                            if gender_label[0]=="female":    
                                send_telegram_alert(frame,"stress")
                        # Perform gender classification
                        gender_label = classify_gender(person_image)
                        print(f"Gender for objectID {objectID}: {gender_label}")

        # Detect genders for each detected person
        try:
            gender_counts = detect_genders_in_frame(frame, person_boxes)
            male_count = gender_counts.get("males", 0)
            female_count = gender_counts.get("females", 0)
        except Exception as e:
            print(f"Error in gender detection: {e}")
            male_count = female_count = 0

        print(f"Number of males: {male_count}, Number of females: {female_count}, Total persons: {n}")

        # Display counts on the frame
        count_text = f'Males: {male_count}  Females: {female_count}  Total Persons: {n}'
        cv2.putText(frame, count_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Alert condition: Female detected alone
        if female_count == 1 and male_count == 0:
            send_telegram_alert(frame, "Female detected alone at night!")
            print("Alert sent: Female detected alone at night.")

        # Alert condition: Female surrounded by males
        if female_count > 0 and n > 0:
            try:
                # Store bounding boxes of females (only coordinates)
                female_bboxes = [
                    (x1, y1, x2, y2) for x1, y1, x2, y2 in person_boxes
                    if "female" == classify_gender(frame[y1:y2, x1:x2])[0].lower()
                ]
                
                # Store bounding boxes of males (only coordinates)
                male_bboxes = [
                    (x1, y1, x2, y2) for x1, y1, x2, y2 in person_boxes
                    if "male" == classify_gender(frame[y1:y2, x1:x2])[0].lower()
                ]

                #process_faces(frame, female_bboxes, male_bboxes)


                # process_faces()
                # for i in male_bboxes:
                #     print("the emotion of male is :",classify_face(i))
                # for i in female_bboxes:
                #     print("the emotion of female is :",classify_face(i))
                # Pass the coordinates to is_female_surrounded function
                if process_frame(frame, female_bboxes, male_bboxes):
                    send_telegram_alert(frame, "Female surrounded by men, potential danger detected!")
                    print("Alert sent: Female surrounded by men.")
            except Exception as e:
                print(f"Error in is_female_surrounded logic: {e}")


        # Annotate bounding boxes for detected persons
        for i, box in enumerate(person_boxes):
            x1, y1, x2, y2 = map(int, box)
            label = f"Person {i + 1}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show the processed video frame
        cv2.imshow("Webcam/Video Feed", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Release resources
    webcam.release()
    cv2.destroyAllWindows()
