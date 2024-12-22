import cv2
import numpy as np
import urllib.request
from ultralytics import YOLO

# Replace with your ESP32-CAM's stream URL
esp32_cam_url = "http://192.168.4.1/stream"
# Load YOLO model
model = YOLO("yolo-Weights/yolov8n.pt")

# Object classes
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]

# Open the MJPEG stream using urllib
stream = urllib.request.urlopen(esp32_cam_url)

# Initialize a buffer for the MJPEG frames
bytes_buffer = b''

while True:
    try:
        # Read data from the stream in chunks
        bytes_buffer += stream.read(1024)
        
        # Find the start and end of the JPEG frame
        start = bytes_buffer.find(b'\xff\xd8')  # Start of JPEG
        end = bytes_buffer.find(b'\xff\xd9')    # End of JPEG

        if start != -1 and end != -1:
            # Extract the JPEG frame
            jpg = bytes_buffer[start:end + 2]
            bytes_buffer = bytes_buffer[end + 2:]

            # Decode the JPEG frame to a numpy array
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            # Run YOLO model on the frame
            results = model(img, stream=True)

            # Process detections
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    # Bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    # Draw bounding box
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                    # Confidence
                    confidence = round(box.conf[0], 2)

                    # Class name
                    cls = int(box.cls[0])

                    # Display class name and confidence
                    label = f"{classNames[cls]} {confidence:.2f}"
                    cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Show the processed frame
            cv2.imshow('ESP32-CAM Stream', img)

            # Press 'q' to exit
            if cv2.waitKey(1) == ord('q'):
                break

    except Exception as e:
        print(f"Error reading frame: {e}")
        break

cv2.destroyAllWindows()
