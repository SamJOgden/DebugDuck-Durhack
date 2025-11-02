"""
FER Service for Debug Duck Pi-Sentry
Background facial emotion recognition monitoring
Triggers empathy response when frustration is detected
"""

import cv2
import numpy as np
import tensorflow.lite as tflite
from picamera2 import Picamera2
import time
import os
import requests
from dotenv import load_dotenv
import logging
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
EMOTION_MODEL_PATH = os.environ.get("EMOTION_MODEL_PATH", "assets/emotion-model.tflite")
FACE_CASCADE_PATH = os.environ.get("FACE_CASCADE_PATH", "haarcascade_frontalface_default.xml")
FRUSTRATION_THRESHOLD = int(os.environ.get("FER_FRUSTRATION_THRESHOLD", 100))
FRAME_SKIP = int(os.environ.get("FER_FRAME_SKIP", 2))
CONFIDENCE_THRESHOLD = float(os.environ.get("FER_CONFIDENCE_THRESHOLD", 0.5))

# Emotions list
EMOTIONS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

# Emotions that indicate frustration
FRUSTRATION_EMOTIONS = ["angry", "disgust", "sad"]


class FERService:
    """
    Facial Emotion Recognition Service
    Runs in background, monitors for frustration, triggers empathy endpoint
    """

    def __init__(self, empathy_callback=None):
        """
        Initialize FER Service

        Args:
            empathy_callback: Function to call when frustration is detected
        """
        self.empathy_callback = empathy_callback
        self.running = False
        self.frustration_counter = 0
        self.thread = None

        # Load models
        self._load_models()

        # Initialize camera
        self.picam2 = None

        logger.info("FER Service initialized")

    def _load_models(self):
        """Load TFLite emotion model and face detection cascade"""
        try:
            # Load TFLite model
            self.interpreter = tflite.Interpreter(model_path=EMOTION_MODEL_PATH)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            # Get model input shape
            input_shape = self.input_details[0]['shape']
            self.img_height = input_shape[1]
            self.img_width = input_shape[2]

            logger.info(f"Emotion model loaded. Input shape: {self.img_width}x{self.img_height}")

            # Load face detection cascade
            self.face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
            if self.face_cascade.empty():
                raise Exception(f"Failed to load cascade from {FACE_CASCADE_PATH}")

            logger.info("Face detection model loaded")

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

    def _init_camera(self):
        """Initialize picamera2"""
        try:
            self.picam2 = Picamera2()

            # Configure for video capture
            config = self.picam2.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            self.picam2.configure(config)

            # Start camera
            self.picam2.start()

            # Warm up
            time.sleep(2)

            logger.info("✅ Camera initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing camera: {e}")
            return False

    def detect_emotion(self, frame_bgr):
        """
        Detect emotion in a single frame

        Args:
            frame_bgr: Frame in BGR format

        Returns:
            str: Detected emotion, or None if no face found
        """
        # Convert to grayscale
        gray_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray_frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        if len(faces) == 0:
            return None

        # Process first face only
        (x, y, w, h) = faces[0]

        # Extract face region from BGR frame (color, not grayscale!)
        face_roi_bgr = frame_bgr[y:y+h, x:x+w]

        # Preprocess for FER model
        roi_resized = cv2.resize(face_roi_bgr, (self.img_width, self.img_height))
        roi_normalized = roi_resized.astype('float32') / 255.0
        roi_final = np.expand_dims(roi_normalized, axis=0)
        # Note: No second expand_dims needed for color images

        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], roi_final)
        self.interpreter.invoke()

        # Get prediction
        predictions = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

        # Get dominant emotion
        emotion_index = np.argmax(predictions)
        confidence = np.max(predictions)

        # Only return if confidence is above threshold
        if confidence >= CONFIDENCE_THRESHOLD:
            return EMOTIONS[emotion_index]
        else:
            return None

    def _monitor_loop(self):
        """Main monitoring loop (runs in background thread)"""
        logger.info("FER monitoring started")

        frame_count = 0

        try:
            while self.running:
                # Capture frame
                frame = self.picam2.capture_array()

                # Convert RGB to BGR
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # Skip frames for performance
                if frame_count % FRAME_SKIP == 0:
                    emotion = self.detect_emotion(frame_bgr)

                    if emotion:
                        logger.debug(f"Detected: {emotion}")

                        # Check if emotion indicates frustration
                        if emotion in FRUSTRATION_EMOTIONS:
                            self.frustration_counter += 1
                            logger.info(f"Frustration detected ({self.frustration_counter}/{FRUSTRATION_THRESHOLD})")

                            # Trigger empathy if threshold reached
                            if self.frustration_counter >= FRUSTRATION_THRESHOLD:
                                logger.warning("🔥 FRUSTRATION THRESHOLD REACHED!")
                                self._trigger_empathy()
                                # Reset counter after triggering
                                self.frustration_counter = 0
                        else:
                            # Reset counter if emotion is not frustration
                            if self.frustration_counter > 0:
                                self.frustration_counter = max(0, self.frustration_counter - 2)

                frame_count += 1

                # Small delay
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")

        finally:
            logger.info("FER monitoring stopped")

    def _trigger_empathy(self):
        """Trigger empathy response (call the callback or Flask endpoint)"""
        logger.info("Triggering empathy response...")

        if self.empathy_callback:
            try:
                self.empathy_callback()
            except Exception as e:
                logger.error(f"Error in empathy callback: {e}")
        else:
            # If no callback, try to call local Flask endpoint
            try:
                response = requests.get("http://localhost:5000/trigger-empathy", timeout=5)
                if response.status_code == 200:
                    logger.info("Empathy triggered successfully")
                else:
                    logger.error(f"Empathy trigger failed: {response.status_code}")
            except Exception as e:
                logger.error(f"Error triggering empathy endpoint: {e}")

    def start(self):
        """Start the FER monitoring service"""
        if self.running:
            logger.warning("FER service already running")
            return False

        # Initialize camera
        if not self._init_camera():
            logger.error("Failed to initialize camera. FER service not started.")
            return False

        # Start monitoring thread
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

        logger.info("✅ FER Service started")
        return True

    def stop(self):
        """Stop the FER monitoring service"""
        if not self.running:
            logger.warning("FER service not running")
            return

        logger.info("Stopping FER service...")
        self.running = False

        # Wait for thread to finish
        if self.thread:
            self.thread.join(timeout=5)

        # Stop camera
        if self.picam2:
            self.picam2.stop()

        logger.info("✅ FER Service stopped")


# Test the FER service
if __name__ == "__main__":
    print("\n=== Testing FER Service ===\n")

    def test_empathy_callback():
        print("🦆 EMPATHY TRIGGERED! Duck would speak comforting phrase here.")

    # Create service with test callback
    fer = FERService(empathy_callback=test_empathy_callback)

    # Start monitoring
    if fer.start():
        print("FER monitoring is running...")
        print("Make frustrated faces at the camera to test!")
        print("Press Ctrl+C to stop\n")

        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")

        fer.stop()
        print("Test complete!")
    else:
        print("Failed to start FER service")
