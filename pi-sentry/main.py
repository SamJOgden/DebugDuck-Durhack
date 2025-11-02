#!/usr/bin/env python3
"""
Debug Duck Pi-Sentry - Main Application
Orchestrates all services: GUI, FER, Button Listener, and Flask Server
"""

import os
import sys
import time
import signal
import logging
from threading import Thread
from dotenv import load_dotenv

# Import all services
from duck_gui import DuckGUI
from fer_service import FERService
from button_listener import ButtonListener
import sentry_server

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
PI_HOST = os.environ.get("PI_HOST", "0.0.0.0")
PI_PORT = int(os.environ.get("PI_PORT", 5000))


class DebugDuck:
    """
    Main Debug Duck Application
    Manages all services and coordinates their interactions
    """

    def __init__(self):
        self.gui = None
        self.fer = None
        self.button = None
        self.flask_thread = None
        self.running = False

        logger.info("=" * 60)
        logger.info("DEBUG DUCK - MAIN APPLICATION")
        logger.info("=" * 60)

    def _empathy_callback(self):
        """Callback for when FER detects frustration"""
        logger.info("FER triggered empathy callback")

        # Trigger empathy endpoint
        import requests
        try:
            requests.get(f"http://localhost:{PI_PORT}/trigger-empathy", timeout=5)
        except Exception as e:
            logger.error(f"Error calling empathy endpoint: {e}")

    def _button_callback(self):
        """Callback for when button is pressed"""
        logger.info("Button triggered callback")

        # Change GUI to listening
        if self.gui:
            self.gui.set_emotion("listening")

        # Button will call laptop client directly (configured in button_listener.py)

    def start_services(self):
        """Start all services"""
        logger.info("\nStarting services...\n")

        # 1. Start GUI
        try:
            logger.info("[1/4] Starting Duck GUI...")
            self.gui = DuckGUI(fullscreen=True)
            if self.gui.start():
                logger.info("✅ Duck GUI started")
            else:
                logger.error("❌ Failed to start Duck GUI")
                return False
        except Exception as e:
            logger.error(f"❌ Error starting GUI: {e}")
            logger.warning("Continuing without GUI...")
            self.gui = None

        # Give GUI time to initialize
        time.sleep(1)

        # 2. Set GUI reference in Flask server
        if self.gui:
            sentry_server.set_gui(self.gui)

        # 3. Start FER Service
        try:
            logger.info("[2/4] Starting FER Service...")
            self.fer = FERService(empathy_callback=self._empathy_callback)
            if self.fer.start():
                logger.info("✅ FER Service started")
            else:
                logger.error("❌ Failed to start FER Service")
                logger.warning("Continuing without FER...")
                self.fer = None
        except Exception as e:
            logger.error(f"❌ Error starting FER: {e}")
            logger.warning("Continuing without FER...")
            self.fer = None

        # 4. Start Button Listener
        try:
            logger.info("[3/4] Starting Button Listener...")
            self.button = ButtonListener(button_callback=self._button_callback)
            if self.button.start():
                logger.info("✅ Button Listener started")
            else:
                logger.error("❌ Failed to start Button Listener")
                logger.warning("Continuing without button...")
                self.button = None
        except Exception as e:
            logger.error(f"❌ Error starting Button Listener: {e}")
            logger.warning("Continuing without button...")
            self.button = None

        # 5. Start Flask Server (in separate thread)
        try:
            logger.info("[4/4] Starting Flask Server...")

            def run_flask():
                sentry_server.app.run(
                    host=PI_HOST,
                    port=PI_PORT,
                    debug=False,  # Disable debug mode when running with other services
                    use_reloader=False  # Disable reloader to avoid thread conflicts
                )

            self.flask_thread = Thread(target=run_flask, daemon=True)
            self.flask_thread.start()

            # Give Flask time to start
            time.sleep(2)

            logger.info("✅ Flask Server started")
        except Exception as e:
            logger.error(f"❌ Error starting Flask server: {e}")
            return False

        logger.info("\n" + "=" * 60)
        logger.info("✅ ALL SERVICES STARTED")
        logger.info("=" * 60)
        logger.info(f"Flask server running on http://{PI_HOST}:{PI_PORT}")
        logger.info("GUI displaying on touchscreen")
        if self.fer:
            logger.info("FER monitoring active")
        if self.button:
            logger.info("Button listener active")
        logger.info("\nDebug Duck is ready! 🦆")
        logger.info("=" * 60 + "\n")

        self.running = True
        return True

    def stop_services(self):
        """Stop all services gracefully"""
        logger.info("\n" + "=" * 60)
        logger.info("SHUTTING DOWN DEBUG DUCK")
        logger.info("=" * 60)

        self.running = False

        # Stop FER
        if self.fer:
            logger.info("Stopping FER Service...")
            self.fer.stop()

        # Stop Button Listener
        if self.button:
            logger.info("Stopping Button Listener...")
            self.button.stop()

        # Stop GUI
        if self.gui:
            logger.info("Stopping Duck GUI...")
            self.gui.stop()

        # Flask will stop when the main thread exits
        logger.info("Flask server will stop with main thread")

        logger.info("=" * 60)
        logger.info("✅ Debug Duck shut down complete")
        logger.info("=" * 60)

    def run(self):
        """Main run loop"""
        # Start all services
        if not self.start_services():
            logger.error("Failed to start services. Exiting.")
            return 1

        # Set up signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("\nReceived shutdown signal...")
            self.stop_services()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nKeyboard interrupt received...")
            self.stop_services()

        return 0


def main():
    """Entry point"""
    # Check if running as root (needed for GPIO on some systems)
    if os.geteuid() != 0:
        logger.warning("⚠️  Not running as root. GPIO may not work.")
        logger.warning("   Consider running with: sudo python3 main.py")
        logger.warning("   Or add user to gpio group: sudo usermod -a -G gpio $USER")

    # Create and run the Debug Duck
    duck = DebugDuck()
    return duck.run()


if __name__ == "__main__":
    sys.exit(main())
