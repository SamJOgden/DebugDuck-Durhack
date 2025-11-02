"""
Test script to compare BGR vs Grayscale preprocessing
Helps determine which input format the emotion model was trained on
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

    # Get model input shape
    input_shape = input_details[0]['shape']
    IMG_HEIGHT = input_shape[1]
    IMG_WIDTH = input_shape[2]
    print(f"Model input shape: {input_shape}")

    # Load OpenCV model for face detection
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Define the emotions
    EMOTIONS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

except Exception as e:
    print(f"Error loading models: {e}")
    exit()


# --- Start PiCamera2 ---
try:
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    print("Camera started. Press Ctrl+C to quit.\n")
    time.sleep(1)
except Exception as e:
    print(f"Error starting picamera2: {e}")
    exit()


def test_preprocessing(face_roi, mode="BGR"):
    """
    Test emotion detection with different preprocessing

    Args:
        face_roi: Face region to test
        mode: "BGR" or "GRAY"
    """
    if mode == "GRAY":
        # Grayscale preprocessing
        if len(face_roi.shape) == 3:
            face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        else:
            face_gray = face_roi
        roi_resized = cv2.resize(face_gray, (IMG_WIDTH, IMG_HEIGHT))
        roi_normalized = roi_resized.astype('float32') / 255.0
        roi_final = np.expand_dims(roi_normalized, axis=0)
        roi_final = np.expand_dims(roi_final, axis=-1)  # Add channel dimension
    else:  # BGR
        # Color preprocessing
        roi_resized = cv2.resize(face_roi, (IMG_WIDTH, IMG_HEIGHT))
        roi_normalized = roi_resized.astype('float32') / 255.0
        roi_final = np.expand_dims(roi_normalized, axis=0)

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], roi_final)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])[0]

    return predictions


# --- Main Loop ---
print("Capturing a frame with a face to compare preprocessing methods...\n")
frame_count = 0

while frame_count < 10:  # Try for 10 frames
    try:
        # Capture frame from picamera2
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        gray_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            print(f"\n{'='*80}")
            print(f"Frame {frame_count}: Face detected!")
            print(f"{'='*80}\n")

            # Get first face
            (x, y, w, h) = faces[0]
            face_roi_bgr = frame_bgr[y:y+h, x:x+w]

            # Test BGR preprocessing
            print("Testing BGR (color) preprocessing:")
            predictions_bgr = test_preprocessing(face_roi_bgr, mode="BGR")
            emotion_bgr = EMOTIONS[np.argmax(predictions_bgr)]
            confidence_bgr = np.max(predictions_bgr)
            print(f"  Dominant emotion: {emotion_bgr} (confidence: {confidence_bgr:.3f})")
            print(f"  All scores: {dict(zip(EMOTIONS, [f'{p:.3f}' for p in predictions_bgr]))}")

            # Test GRAY preprocessing
            print("\nTesting GRAYSCALE preprocessing:")
            predictions_gray = test_preprocessing(face_roi_bgr, mode="GRAY")
            emotion_gray = EMOTIONS[np.argmax(predictions_gray)]
            confidence_gray = np.max(predictions_gray)
            print(f"  Dominant emotion: {emotion_gray} (confidence: {confidence_gray:.3f})")
            print(f"  All scores: {dict(zip(EMOTIONS, [f'{p:.3f}' for p in predictions_gray]))}")

            # Compare
            print("\n" + "="*80)
            if confidence_bgr > confidence_gray:
                print(f"✅ BGR works better! ({confidence_bgr:.3f} vs {confidence_gray:.3f})")
            else:
                print(f"✅ GRAYSCALE works better! ({confidence_gray:.3f} vs {confidence_bgr:.3f})")
            print("="*80 + "\n")

            time.sleep(2)  # Wait before next capture

        frame_count += 1
        time.sleep(0.5)

    except KeyboardInterrupt:
        break

picam2.stop()
print("\nCamera stopped.")
