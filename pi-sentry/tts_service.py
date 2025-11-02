"""
TTS Service for Debug Duck Pi-Sentry
Uses Piper TTS to make the duck speak
"""

import subprocess
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get TTS configuration from environment
PIPER_EXECUTABLE = os.environ.get("PIPER_EXECUTABLE_PATH", "./piper/piper")
PIPER_VOICE_MODEL = os.environ.get("PIPER_VOICE_MODEL", "./piper/en_US-lessac-medium.onnx")


def speak(text):
    """
    Convert text to speech and play it through the speaker.

    Args:
        text (str): The text for the duck to speak

    Returns:
        bool: True if speech was successful, False otherwise
    """
    if not text or not text.strip():
        logger.warning("Empty text provided to speak()")
        return False

    logger.info(f"Speaking: '{text}'")

    try:
        # Check if Piper executable exists
        if not os.path.exists(PIPER_EXECUTABLE):
            logger.error(f"Piper executable not found at: {PIPER_EXECUTABLE}")
            logger.error("Run setup_pi.sh to install Piper TTS")
            return False

        # Check if voice model exists
        if not os.path.exists(PIPER_VOICE_MODEL):
            logger.error(f"Voice model not found at: {PIPER_VOICE_MODEL}")
            logger.error("Run setup_pi.sh to download voice model")
            return False

        # Build the command pipeline: echo text | piper | aplay
        # Use subprocess.run with shell=True to handle the pipe
        command = f'echo "{text}" | {PIPER_EXECUTABLE} --model {PIPER_VOICE_MODEL} --output_file - | aplay'

        # Run the command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # Increased for longer AI responses
        )

        if result.returncode == 0:
            logger.info("Speech completed successfully")
            return True
        else:
            logger.error(f"Speech failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Error output: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("Speech timeout - command took too long")
        return False
    except Exception as e:
        logger.error(f"Error during speech: {e}")
        return False


def speak_async(text):
    """
    Convert text to speech and play it asynchronously (non-blocking).
    Useful when you don't want to wait for speech to complete.

    Args:
        text (str): The text for the duck to speak

    Returns:
        subprocess.Popen: The process object, or None on error
    """
    if not text or not text.strip():
        logger.warning("Empty text provided to speak_async()")
        return None

    logger.info(f"Speaking async: '{text}'")

    try:
        # Check if Piper executable exists
        if not os.path.exists(PIPER_EXECUTABLE):
            logger.error(f"Piper executable not found at: {PIPER_EXECUTABLE}")
            return None

        # Check if voice model exists
        if not os.path.exists(PIPER_VOICE_MODEL):
            logger.error(f"Voice model not found at: {PIPER_VOICE_MODEL}")
            return None

        # Build the command pipeline
        command = f'echo "{text}" | {PIPER_EXECUTABLE} --model {PIPER_VOICE_MODEL} --output_file - | aplay'

        # Start the process in the background
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        logger.info(f"Speech started (PID: {process.pid})")
        return process

    except Exception as e:
        logger.error(f"Error starting async speech: {e}")
        return None


def test_audio():
    """
    Test if audio output is working.

    Returns:
        bool: True if audio test passed, False otherwise
    """
    logger.info("Testing audio output...")

    try:
        # Simple speaker test using aplay
        result = subprocess.run(
            ["speaker-test", "-t", "wav", "-c", "2", "-l", "1"],
            capture_output=True,
            timeout=5
        )

        if result.returncode == 0:
            logger.info("✅ Audio output working")
            return True
        else:
            logger.error("❌ Audio output test failed")
            return False

    except subprocess.TimeoutExpired:
        logger.error("Audio test timed out")
        return False
    except FileNotFoundError:
        logger.error("speaker-test command not found")
        logger.info("Try: sudo apt install alsa-utils")
        return False
    except Exception as e:
        logger.error(f"Error testing audio: {e}")
        return False


# Test the TTS service
if __name__ == "__main__":
    print("\n=== Testing TTS Service ===\n")

    # Test 1: Check audio output
    print("Test 1: Checking audio output...")
    test_audio()
    print("")

    # Test 2: Speak a test phrase (synchronous)
    print("Test 2: Testing synchronous speech...")
    success = speak("Hello! I am the Debug Duck. Ready to help you code!")
    if success:
        print("✅ Synchronous speech test passed")
    else:
        print("❌ Synchronous speech test failed")
    print("")

    # Test 3: Speak asynchronously
    print("Test 3: Testing asynchronous speech...")
    process = speak_async("This is an asynchronous speech test.")
    if process:
        print(f"✅ Async speech started (PID: {process.pid})")
        print("Waiting for speech to complete...")
        process.wait()
        print("✅ Async speech completed")
    else:
        print("❌ Async speech test failed")
    print("")

    print("=== TTS Test Complete ===")
