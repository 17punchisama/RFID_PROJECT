from ultralytics import YOLO
import cv2
import math
import paho.mqtt.client as mqtt
import json

# Initialize MQTT client
mqtt_broker = "broker.hivemq.com"  # Replace with your MQTT broker
mqtt_port = 1883  # Default MQTT port
mqtt_topic = "zerotohero/esl/punyee"

client = mqtt.Client()
client.connect(mqtt_broker, mqtt_port, 60)
client.loop_start()

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set width
cap.set(4, 320)  # Set height

# Load YOLO model
model = YOLO("testt.pt")

# Define object classes
classNames = ["Junior", "Punyee", 'Tonfah']

# Variables to keep track of the last published state and count
last_detected_class = None
count = 0

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image from webcam.")
        break

    # Perform object detection
    results = model(img)

    # Variable to keep track of detected objects
    detected_objects = []

    # Process detections
    for r in results:
        boxes = r.boxes

        for box in boxes:
            # Extract bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].int().tolist()

            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # Extract and print confidence
            confidence = math.ceil(box.conf[0].item() * 100) / 100
            print(f"Confidence: {confidence}")

            # Extract and print class name
            cls = int(box.cls[0].item())
            class_name = classNames[cls]
            print(f"Class name: {class_name}")

            # Add detected object info to the list
            detected_objects.append({
                "class": class_name,
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2]
            })

            # Increment count if the same class is detected consecutively
            if last_detected_class == class_name:
                count += 1
            else:
                last_detected_class = class_name
                count = 1  # Reset the count if a different class is detected

            print(f"Count for class '{class_name}': {count}")

            # Annotate class name on the image
            org = (x1, y1 - 10)
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 0.5
            color = (255, 0, 0)
            thickness = 1
            cv2.putText(img, class_name, org, font, fontScale, color, thickness)

    # Check if count is greater than or equal to 100 before sending to MQTT
    if detected_objects and count >= 100:
        mqtt_message = last_detected_class
        mqtt_message_json = json.dumps(mqtt_message)

        # Publish to MQTT broker
        result = client.publish(mqtt_topic, mqtt_message_json)
        status = result[0]
        if status == 0:
            print(f"MQTT message sent: {mqtt_message_json}")
        else:
            print(f"Failed to send message to topic {mqtt_topic}")

        # Reset count after publishing
        count = 0

    # Display the resulting frame
    cv2.imshow('Webcam', img)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
