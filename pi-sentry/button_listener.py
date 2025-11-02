"""
Button Listener for Debug Duck Pi-Sentry
Listens for physical button presses and triggers help requests to laptop
"""

# Try to import gpiod (for Pi 5), fall back to RPi.GPIO (for older Pi)
try:
    import gpiod
    GPIO_LIB = 'gpiod'
except ImportError:
    try:
        import RPi.GPIO as GPIO
        GPIO_LIB = 'RPi.GPIO'
    except ImportError:
        GPIO_LIB = None

import time
import requests
import os
from dotenv import load_dotenv
import logging
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
BUTTON_PIN = int(os.environ.get("BUTTON_GPIO_PIN", 17))
DEBOUNCE_TIME = float(os.environ.get("BUTTON_DEBOUNCE_TIME", 1.0))
LAPTOP_CLIENT_URL = os.environ.get("LAPTOP_CLIENT_URL", "http://YOUR_LAPTOP_IP:5001/get-help")


class ButtonListener:
    """
    GPIO Button Listener
    Monitors button presses and triggers help requests to laptop client
    """

    def __init__(self, button_callback=None):
        """
        Initialize Button Listener

        Args:
            button_callback: Function to call when button is pressed
        """
        self.button_callback = button_callback
        self.running = False
        self.thread = None
        self.last_press_time = 0

        # Set up GPIO
        self._setup_gpio()

        logger.info("Button Listener initialized")

    def _setup_gpio(self):
        """Set up GPIO pins for button"""
        try:
            # Use BCM pin numbering
            GPIO.setmode(GPIO.BCM)

            # Set up GPIO 17 as input with pull-down resistor
            # DFR0029 module outputs HIGH when pressed
            GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            logger.info(f"✅ GPIO initialized: Button on GPIO {BUTTON_PIN}")

        except Exception as e:
            logger.error(f"❌ Error setting up GPIO: {e}")
            raise

    def _handle_button_press(self):
        """Handle button press (with debouncing)"""
        current_time = time.time()

        # Debounce: ignore if pressed too recently
        if current_time - self.last_press_time < DEBOUNCE_TIME:
            logger.debug("Button press ignored (debounce)")
            return

        self.last_press_time = current_time

        logger.info("🔘 BUTTON PRESSED!")

        # Call callback if provided
        if self.button_callback:
            try:
                self.button_callback()
            except Exception as e:
                logger.error(f"Error in button callback: {e}")
        else:
            # Default action: trigger laptop client
            self._trigger_laptop_help()

    def _trigger_laptop_help(self):
        """Send help request to laptop client"""
        logger.info(f"Sending help request to: {LAPTOP_CLIENT_URL}")

        try:
            response = requests.get(LAPTOP_CLIENT_URL, timeout=30)

            if response.status_code == 200:
                logger.info("✅ Help request successful")
                logger.debug(f"Response: {response.json()}")
            else:
                logger.error(f"❌ Help request failed: HTTP {response.status_code}")

        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Could not connect to laptop at {LAPTOP_CLIENT_URL}")
            logger.error("Make sure:")
            logger.error("1. Laptop client server is running")
            logger.error("2. Laptop IP is correct in .env file")
            logger.error("3. Both devices are on same network")

        except requests.exceptions.Timeout:
            logger.error("❌ Request to laptop timed out")

        except Exception as e:
            logger.error(f"❌ Error sending help request: {e}")

    def _monitor_loop(self):
        """Main monitoring loop using edge detection"""
        logger.info("Button monitoring started")

        try:
            while self.running:
                # Wait for rising edge (button press)
                # This will block until button is pressed or timeout (1 second)
                channel = GPIO.wait_for_edge(BUTTON_PIN, GPIO.RISING, timeout=1000)

                if channel is not None:
                    # Button was pressed
                    self._handle_button_press()

        except Exception as e:
            logger.error(f"Error in button monitoring loop: {e}")

        finally:
            logger.info("Button monitoring stopped")

    def start(self):
        """Start button monitoring (runs in background thread)"""
        if self.running:
            logger.warning("Button Listener already running")
            return False

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

        logger.info("✅ Button Listener started")
        return True

    def stop(self):
        """Stop button monitoring"""
        if not self.running:
            logger.warning("Button Listener not running")
            return

        logger.info("Stopping Button Listener...")
        self.running = False

        # Wait for thread to finish
        if self.thread:
            self.thread.join(timeout=5)

        # Clean up GPIO
        GPIO.cleanup()

        logger.info("✅ Button Listener stopped")


# Test the button listener
if __name__ == "__main__":
    print("\n=== Testing Button Listener ===\n")

    def test_button_callback():
        print("🦆 BUTTON CALLBACK TRIGGERED!")
        print("In the real app, this would call the laptop client.")

    # Create listener with test callback
    listener = ButtonListener(button_callback=test_button_callback)

    # Start listening
    if listener.start():
        print(f"Button listener is running on GPIO {BUTTON_PIN}...")
        print("Press the physical button to test!")
        print("Press Ctrl+C to stop\n")

        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")

        listener.stop()
        print("Test complete!")
    else:
        print("Failed to start button listener")
