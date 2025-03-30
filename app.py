from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
import uvicorn
import cv2
import numpy as np
import json

app = FastAPI()

# Load the trained YOLOv12 model
model = YOLO("yolov12l.pt")  # Ensure this file is uploaded

# Define the classes you want to detect
TARGET_CLASSES = [1, 2, 3, 5, 7]  # 1 = Auto-rickshaw, 2 = Car, 3 = Motorcycle, etc.

def process_image(image_bytes):
    """ Process uploaded image & return vehicle count & types """
    image_np = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # Run YOLO detection with class filtering
    results = model(image, conf=0.3, classes=TARGET_CLASSES)  

    vehicle_count = 0
    vehicle_types = {}

    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])  # Get class ID
            if cls_id in TARGET_CLASSES:  # Filter only selected classes
                class_name = result.names[cls_id]  # Get class name

                # Count vehicles
                vehicle_count += 1
                if class_name in vehicle_types:
                    vehicle_types[class_name] += 1
                else:
                    vehicle_types[class_name] = 1

    return {"total_vehicles": vehicle_count, "vehicle_types": vehicle_types}

@app.post("/detect")
async def detect_vehicles(file: UploadFile = File(...)):
    """ API to process image & return vehicle details """
    image_bytes = await file.read()
    result = process_image(image_bytes)
    return json.dumps(result, indent=4)

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
