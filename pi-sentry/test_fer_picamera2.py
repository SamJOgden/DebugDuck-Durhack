"""
Test Facial Emotion Recognition with picamera2
Uses picamera2 (libcamera) instead of cv2.VideoCapture for Raspberry Pi camera access
"""

import cv2
import numpy as np
import tensorflow.lite as tflite
from picamera2 import Picamera2
import time

# --- Load Models ---
try:
    # Load TFLite model for emotions
    interpreter = tflite.Interpreter(model_path="assets/emotion-model.tflite")
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Get model input shape (e.g., 48x48 or 64x64)
    input_shape = input_details[0]['shape']
    IMG_HEIGHT = input_shape[1]
    IMG_WIDTH = input_shape[2]

    print(f"Emotion model loaded. Input shape: {IMG_WIDTH}x{IMG_HEIGHT}")

    # Load OpenCV model for face detection
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        raise Exception("Failed to load haarcascade_frontalface_default.xml")

    print("Face detection model loaded.")

    # Define the emotions (this MUST match your model's training)
    EMOTIONS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

except Exception as e:
    print(f"Error loading models: {e}")
    print("Make sure 'haarcascade_frontalface_default.xml' is in pi-sentry/")
    print("And 'emotion-model.tflite' is in assets/")
    exit()


# --- Initialize picamera2 ---
print("Initializing Raspberry Pi Camera with picamera2...")
try:
    picam2 = Picamera2()

    # Configure camera for video capture
    # Using a smaller resolution for faster processing
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
    picam2.configure(config)

    # Start camera
    picam2.start()

    # Give camera time to warm up
    time.sleep(2)

    print("✅ Camera initialized successfully!")
    print("Press Ctrl+C to quit.")

except Exception as e:
    print(f"❌ Error initializing camera: {e}")
    print("\nTroubleshooting:")
    print("1. Is the camera connected properly?")
    print("2. Is libcamera installed? Run: libcamera-hello --list-cameras")
    print("3. Is picamera2 installed? Run: python3 -c 'from picamera2 import Picamera2'")
    exit()


# --- Main FER Loop ---
frame_count = 0
last_print_time = time.time()
fps = 0

try:
    while True:
        # Capture frame from camera
        frame = picam2.capture_array()

        # picamera2 returns RGB, OpenCV expects BGR
        # Convert RGB to BGR for OpenCV processing
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Convert to grayscale for face detection
        gray_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray_frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Process each face
        for (x, y, w, h) in faces:
            # Extract the face region
            face_roi_gray = gray_frame[y:y+h, x:x+w]

            # --- Preprocess for FER Model ---
            # 1. Resize to the model's expected input size
            roi_resized = cv2.resize(face_roi_gray, (IMG_WIDTH, IMG_HEIGHT))
            # 2. Normalize pixel values (common for many models)
            roi_normalized = roi_resized.astype('float32') / 255.0
            # 3. Expand dimensions to match model input (1, 48, 48, 1)
            roi_final = np.expand_dims(roi_normalized, axis=0)
            roi_final = np.expand_dims(roi_final, axis=-1)

            # --- Run Inference ---
            interpreter.set_tensor(input_details[0]['index'], roi_final)
            interpreter.invoke()

            # Get the prediction
            predictions = interpreter.get_tensor(output_details[0]['index'])[0]

            # Get the dominant emotion
            emotion_index = np.argmax(predictions)
            emotion_text = EMOTIONS[emotion_index]
            confidence = np.max(predictions) * 100

            # Print emotion to terminal
            print(f"Detected: {emotion_text} ({confidence:.2f}%) | FPS: {fps:.1f}")

        # Calculate FPS
        frame_count += 1
        current_time = time.time()
        if current_time - last_print_time >= 1.0:
            fps = frame_count / (current_time - last_print_time)
            frame_count = 0
            last_print_time = current_time

        # Small delay to prevent overwhelming the system
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nStopping FER test...")

finally:
    # Clean up camera
    picam2.stop()
    print("Camera stopped. Test complete!")
