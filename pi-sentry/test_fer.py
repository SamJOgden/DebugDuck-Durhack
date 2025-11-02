import cv2
import numpy as np
import tensorflow.lite as tflite

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

    # Load OpenCV model for face detection
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Define the emotions (this MUST match your model's training)
    EMOTIONS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

except Exception as e:
    print(f"Error loading models: {e}")
    print("Make sure 'haarcascade_frontalface_default.xml' is in pi-sentry/")
    print("And 'emotion-model.tflite' is in assets/")
    exit()


# --- Start Camera ---
# Using cv2.VideoCapture(0) is simpler for a test
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open camera.")
    exit()

print("Camera open. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame.")
        break

    # Convert to grayscale for face detection
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Process each face
    for (x, y, w, h) in faces:
        # Draw a rectangle around the face (for our visual test)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Extract face from BGR frame (color, not grayscale!)
        face_roi_bgr = frame[y:y+h, x:x+w]

        # --- Preprocess for FER Model ---
        # 1. Resize to the model's expected input size
        roi_resized = cv2.resize(face_roi_bgr, (IMG_WIDTH, IMG_HEIGHT))
        # 2. Normalize pixel values (common for many models)
        roi_normalized = roi_resized.astype('float32') / 255.0
        # 3. Expand dimensions to match model input (1, 48, 48, 3)
        roi_final = np.expand_dims(roi_normalized, axis=0)
        # Note: No second expand_dims needed for color images

        # --- Run Inference ---
        interpreter.set_tensor(input_details[0]['index'], roi_final)
        interpreter.invoke()

        # Get the prediction
        predictions = interpreter.get_tensor(output_details[0]['index'])[0]

        # Get the dominant emotion
        emotion_index = np.argmax(predictions)
        emotion_text = EMOTIONS[emotion_index]

        # Print emotion to terminal
        print(f"Detected: {emotion_text} ({np.max(predictions)*100:.2f}%)")

    # We can't use cv2.imshow() on a headless Pi,
    # but the print statements in the terminal are our test.
    # This loop will run very fast.

    # A 'q' key listener would require a display, 
    # so for this test, just let it run for a bit and
    # stop it with Ctrl+C in the terminal.

cap.release()