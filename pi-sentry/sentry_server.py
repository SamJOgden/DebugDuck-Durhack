"""
Sentry Server for Debug Duck Pi-Sentry
Flask server that handles empathy triggers and speaking responses
"""

from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import logging
from llm_router import LLMRouter
import tts_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
PI_HOST = os.environ.get("PI_HOST", "0.0.0.0")
PI_PORT = int(os.environ.get("PI_PORT", 5000))

# Flask app
app = Flask(__name__)

# Initialize LLM router
try:
    llm_router = LLMRouter()
    logger.info("LLM Router initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM Router: {e}")
    llm_router = None

# Shared GUI reference (will be set by main.py)
duck_gui = None


def set_gui(gui):
    """Set the GUI reference (called from main.py)"""
    global duck_gui
    duck_gui = gui
    logger.info("GUI reference set")


@app.route('/trigger-empathy', methods=['GET'])
def trigger_empathy():
    """
    Trigger empathy response when FER detects frustration.

    Flow:
    1. Get comforting phrase from LLM
    2. Change duck emotion to "concerned"
    3. Speak the phrase
    4. Reset duck emotion to "neutral"
    """
    logger.info("\n" + "=" * 50)
    logger.info("EMPATHY TRIGGERED")
    logger.info("=" * 50)

    try:
        # Step 1: Get comforting phrase from LLM
        if llm_router:
            logger.info("Getting comforting phrase from LLM...")
            phrase = llm_router.get_comforting_phrase()
        else:
            logger.warning("LLM Router not available, using fallback phrase")
            phrase = "Hey, take a breath. You've got this!"

        logger.info(f"Phrase: {phrase}")

        # Step 2: Change duck emotion to "concerned"
        if duck_gui:
            duck_gui.set_emotion("concerned")

        # Step 3: Speak the phrase
        logger.info("Speaking phrase...")
        tts_service.speak(phrase)

        # Step 4: Reset duck emotion to "neutral" (after a delay)
        if duck_gui:
            import time
            time.sleep(1)
            duck_gui.set_emotion("neutral")

        return jsonify({
            "status": "success",
            "phrase": phrase
        }), 200

    except Exception as e:
        error_msg = f"Error during empathy response: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 500


@app.route('/speak', methods=['POST'])
def speak():
    """
    Speak text sent from the laptop client.

    Expects JSON:
    {
        "text": "Text to speak"
    }
    """
    logger.info("\n" + "=" * 50)
    logger.info("SPEAK REQUEST RECEIVED")
    logger.info("=" * 50)

    try:
        # Get text from request
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({
                "status": "error",
                "message": "No text provided"
            }), 400

        logger.info(f"Text to speak: {text}")

        # Change duck emotion to "listening"
        if duck_gui:
            duck_gui.set_emotion("listening")

        # Speak the text
        success = tts_service.speak(text)

        # Reset duck emotion to "neutral"
        if duck_gui:
            import time
            time.sleep(0.5)
            duck_gui.set_emotion("neutral")

        if success:
            return jsonify({
                "status": "success",
                "text": text
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "TTS failed"
            }), 500

    except Exception as e:
        error_msg = f"Error during speak: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 500


@app.route('/emotion', methods=['POST'])
def set_emotion():
    """
    Manually set duck emotion (for testing/debugging).

    Expects JSON:
    {
        "emotion": "neutral|concerned|listening|happy"
    }
    """
    try:
        data = request.get_json()
        emotion = data.get('emotion', 'neutral')

        logger.info(f"Setting emotion to: {emotion}")

        if duck_gui:
            duck_gui.set_emotion(emotion)
            return jsonify({
                "status": "success",
                "emotion": emotion
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "GUI not initialized"
            }), 500

    except Exception as e:
        error_msg = f"Error setting emotion: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 500


@app.route('/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "service": "Debug Duck Pi-Sentry",
        "port": PI_PORT,
        "llm_router": "initialized" if llm_router else "failed",
        "gui": "initialized" if duck_gui else "not set"
    }), 200


if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("DEBUG DUCK - PI SENTRY SERVER")
    logger.info("=" * 60)
    logger.info(f"Starting Flask server on {PI_HOST}:{PI_PORT}...")
    logger.info("=" * 60 + "\n")

    # Run Flask app
    app.run(
        host=PI_HOST,
        port=PI_PORT,
        debug=True
    )
