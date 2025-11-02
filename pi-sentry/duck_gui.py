"""
Duck GUI for Debug Duck Pi-Sentry
Displays the animated duck on the 7" touchscreen with emotion states
"""

import pygame
import pygame.time
import os
from dotenv import load_dotenv
import logging
import threading
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
DUCK_IMAGE_PATH = os.environ.get("DUCK_IMAGE_PATH", "assets/animations/duck_neutral.png")


class DuckGUI:
    """
    Duck GUI Manager
    Handles displaying the duck and changing its emotional state
    """

    def __init__(self, fullscreen=True):
        """
        Initialize Duck GUI

        Args:
            fullscreen (bool): Whether to run in fullscreen mode
        """
        self.fullscreen = fullscreen
        self.running = False
        self.current_emotion = "neutral"
        self.thread = None

        # Duck images for different emotions
        self.duck_images = {}

        # Initialize pygame
        self._init_pygame()

        logger.info("Duck GUI initialized")

    def _init_pygame(self):
        """Initialize pygame and set up display"""
        try:
            # Set DISPLAY for SSH sessions
            os.environ['DISPLAY'] = ':0'

            pygame.init()

            # Get display info
            display_info = pygame.display.Info()
            self.screen_width = display_info.current_w
            self.screen_height = display_info.current_h

            logger.info(f"Display size: {self.screen_width}x{self.screen_height}")

            # Set up display
            if self.fullscreen:
                self.screen = pygame.display.set_mode(
                    (self.screen_width, self.screen_height),
                    pygame.FULLSCREEN
                )
            else:
                self.screen = pygame.display.set_mode(
                    (800, 480)  # Default 7" screen resolution
                )

            pygame.display.set_caption("Debug Duck")

            # Hide mouse cursor
            pygame.mouse.set_visible(False)

            # Load duck images
            self._load_duck_images()

            logger.info("✅ Pygame initialized successfully")

        except Exception as e:
            logger.error(f"❌ Error initializing pygame: {e}")
            raise

    def _load_duck_images(self):
        """Load duck images for different emotions"""
        # For now, we'll use the same neutral image for all emotions
        # You can add different images for each emotion later
        emotions = ["neutral", "concerned", "listening", "happy"]

        for emotion in emotions:
            try:
                # Try to load specific emotion image
                image_path = f"assets/animations/duck_{emotion}.png"
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path)
                else:
                    # Fall back to neutral image
                    image = pygame.image.load(DUCK_IMAGE_PATH)

                # Scale image to fit screen (maintain aspect ratio)
                image = self._scale_image(image, 400, 400)

                self.duck_images[emotion] = image
                logger.debug(f"Loaded image for emotion: {emotion}")

            except Exception as e:
                logger.error(f"Error loading image for {emotion}: {e}")

                # Create placeholder surface
                self.duck_images[emotion] = pygame.Surface((400, 400))
                self.duck_images[emotion].fill((255, 200, 100))  # Duck yellow color

        logger.info(f"Loaded {len(self.duck_images)} duck images")

    def _scale_image(self, image, max_width, max_height):
        """Scale image to fit within max dimensions while maintaining aspect ratio"""
        image_rect = image.get_rect()
        scale_factor = min(max_width / image_rect.width, max_height / image_rect.height)
        new_width = int(image_rect.width * scale_factor)
        new_height = int(image_rect.height * scale_factor)
        return pygame.transform.scale(image, (new_width, new_height))

    def set_emotion(self, emotion):
        """
        Change the duck's displayed emotion

        Args:
            emotion (str): Emotion to display (neutral, concerned, listening, happy)
        """
        if emotion in self.duck_images:
            self.current_emotion = emotion
            logger.info(f"Duck emotion changed to: {emotion}")
        else:
            logger.warning(f"Unknown emotion: {emotion}, falling back to neutral")
            self.current_emotion = "neutral"

    def _draw(self):
        """Draw the current duck image on screen"""
        # Fill background with a solid color
        self.screen.fill((50, 50, 70))  # Dark blue-gray background

        # Get current duck image
        duck_image = self.duck_images.get(self.current_emotion, self.duck_images["neutral"])

        # Center the image
        duck_rect = duck_image.get_rect()
        duck_rect.center = (self.screen_width // 2, self.screen_height // 2)

        # Draw the duck
        self.screen.blit(duck_image, duck_rect)

        # Update display
        pygame.display.flip()

    def _run_loop(self):
        """Main GUI loop (runs in background thread)"""
        logger.info("Duck GUI started")

        try:
            clock = pygame.time.Clock()
        except AttributeError:
            logger.warning("pygame.Clock not available, using time.sleep fallback")
            clock = None

        try:
            while self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                            self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Touchscreen tap
                        logger.info("Screen tapped")

                # Draw frame
                self._draw()

                # Cap frame rate
                if clock:
                    clock.tick(30)  # 30 FPS
                else:
                    time.sleep(1/30)  # Fallback to 30 FPS with time.sleep

        except Exception as e:
            logger.error(f"Error in GUI loop: {e}")

        finally:
            pygame.quit()
            logger.info("Duck GUI stopped")

    def start(self):
        """Start the GUI (runs in background thread)"""
        if self.running:
            logger.warning("Duck GUI already running")
            return False

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        logger.info("✅ Duck GUI started in background thread")
        return True

    def stop(self):
        """Stop the GUI"""
        if not self.running:
            logger.warning("Duck GUI not running")
            return

        logger.info("Stopping Duck GUI...")
        self.running = False

        # Wait for thread to finish
        if self.thread:
            self.thread.join(timeout=5)

        logger.info("✅ Duck GUI stopped")


# Test the GUI
if __name__ == "__main__":
    import time

    print("\n=== Testing Duck GUI ===\n")

    # Create GUI
    gui = DuckGUI(fullscreen=True)

    # Start GUI
    if gui.start():
        print("GUI is running...")
        print("Testing emotion changes...")

        # Cycle through emotions
        emotions = ["neutral", "concerned", "listening", "happy"]

        try:
            for i in range(3):  # Cycle 3 times
                for emotion in emotions:
                    print(f"Setting emotion: {emotion}")
                    gui.set_emotion(emotion)
                    time.sleep(2)

        except KeyboardInterrupt:
            print("\n\nStopping...")

        gui.stop()
        print("Test complete!")
    else:
        print("Failed to start GUI")
