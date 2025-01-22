import math
from Telebot_Alert import send_telegram_alert
def is_female_surrounded(female_bbox, mbbox, threshold_distance=50):
    surrounding_men_count = 0

    for male_bbox in mbbox:
        # Calculate the distance between the center of the female and male bounding boxes
        male_center_x = (male_bbox[0] + male_bbox[2]) / 2
        male_center_y = (male_bbox[1] + male_bbox[3]) / 2

        female_center_x = (female_bbox[0] + female_bbox[2]) / 2
        female_center_y = (female_bbox[1] + female_bbox[3]) / 2

        distance = math.sqrt((male_center_x - female_center_x) ** 2 + (male_center_y - female_center_y) ** 2)

        # Debug print to check the distances
        print(f"Male bbox: {male_bbox}, Female bbox: {female_bbox}, Distance: {distance}")

        # Check if the male is within the threshold distance
        if distance < threshold_distance:
            surrounding_men_count += 1

        # If we already have two surrounding men, return True
        if surrounding_men_count >= 2:
            return True

    # Return False if fewer than two men are within the threshold distance
    return False
def process_frame(frame, female_bboxes, male_bboxes, threshold_distance=50):
    for female_bbox in female_bboxes:
        # Check if the current female is surrounded
        if is_female_surrounded(female_bbox, male_bboxes, threshold_distance):
            send_telegram_alert(frame, "female_surrounded")
            print("Alert sent: Female surrounded by men.")
            # Trigger the alert

# Dummy implementation of the alert function

