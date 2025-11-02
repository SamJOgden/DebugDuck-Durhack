"""
Client Server for Debug Duck (Laptop)
Flask server that handles help requests from the Raspberry Pi
"""

from flask import Flask, request, jsonify
import requests
from llm_router import LLMRouter
import ocr_service
import pyttsx3
import os

# Initialize TTS engine for laptop
try:
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)  # Speed of speech
    tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    print("TTS engine initialized for laptop speakers")
except Exception as e:
    print(f"WARNING: Could not initialize TTS: {e}")
    tts_engine = None

# Configuration - set to True to speak on laptop instead of Pi
SPEAK_ON_LAPTOP = os.environ.get("SPEAK_ON_LAPTOP", "true").lower() == "true"

# Flask app setup
app = Flask(__name__)

# Initialize the LLM router
try:
    llm_router = LLMRouter()
    print("LLMRouter initialized successfully")
except Exception as e:
    print(f"ERROR: Failed to initialize LLMRouter: {e}")
    llm_router = None

# Configuration
PI_URL = "http://10.249.14.247:5000/speak"
LAPTOP_PORT = 5001


@app.route('/get-help', methods=['GET', 'POST'])
def get_help():
    """
    Main endpoint triggered by the Raspberry Pi when the button is pressed.

    Flow:
    1. Capture screenshot and run OCR
    2. Send code to LLM for analysis
    3. Send response back to Pi to speak
    """
    print("\n" + "=" * 50)
    print("HELP REQUEST RECEIVED from Pi")
    print("=" * 50)

    try:
        # Step 1: Capture screenshot and extract code
        print("Step 1: Capturing screenshot and running OCR...")
        code_text = ocr_service.capture_and_ocr()

        # Check for OCR errors
        if not code_text:
            error_response = "I couldn't read your screen. Make sure there's code visible."
            send_to_pi(error_response)
            return jsonify({
                "status": "error",
                "message": "OCR returned empty result",
                "response": error_response
            }), 500

        if code_text.startswith("Could not capture screen"):
            error_response = "I couldn't capture your screen. Something went wrong."
            send_to_pi(error_response)
            return jsonify({
                "status": "error",
                "message": code_text,
                "response": error_response
            }), 500

        if code_text == "No code detected":
            error_response = "I don't see any code on your screen. Can you make sure your code editor is visible?"
            send_to_pi(error_response)
            return jsonify({
                "status": "error",
                "message": "No text found on screen",
                "response": error_response
            }), 400

        print(f"OCR extracted {len(code_text)} characters")
        print(f"First 200 chars: {code_text[:200]}...")

        # Step 2: Get coding help from LLM
        if not llm_router:
            error_response = "My AI brain isn't working. Check the API key."
            send_to_pi(error_response)
            return jsonify({
                "status": "error",
                "message": "LLMRouter not initialized",
                "response": error_response
            }), 500

        print("Step 2: Getting coding help from LLM...")
        answer = llm_router.get_coding_help(code_text)
        print(f"LLM response: {answer}")

        # Step 3: Speak the answer
        print("Step 3: Speaking response...")
        if SPEAK_ON_LAPTOP:
            # Speak on laptop speakers
            speak_local(answer)
            speak_status = "spoken_on_laptop"
        else:
            # Send to Pi to speak
            pi_response = send_to_pi(answer)
            speak_status = "sent_to_pi" if pi_response else "failed"

        print(f"SUCCESS: Response {speak_status}")
        return jsonify({
            "status": "success",
            "ocr_length": len(code_text),
            "response": answer,
            "speak_status": speak_status
        }), 200

    except Exception as e:
        error_msg = f"Error processing help request: {str(e)}"
        print(f"ERROR: {error_msg}")
        fallback_response = "Oops, something went wrong on my end. Try again?"
        send_to_pi(fallback_response)
        return jsonify({
            "status": "error",
            "message": error_msg,
            "response": fallback_response
        }), 500


@app.route('/get-contextual-help', methods=['POST'])
def get_contextual_help():
    """
    Advanced endpoint for Phase 3: Handles both code and voice question.

    Expects JSON:
    {
        "question": "user's spoken question"
    }
    """
    print("\n" + "=" * 50)
    print("CONTEXTUAL HELP REQUEST RECEIVED from Pi")
    print("=" * 50)

    try:
        # Get the user's question from request
        data = request.get_json()
        user_question = data.get('question', '')

        if not user_question:
            error_response = "I didn't hear a question. Try again?"
            send_to_pi(error_response)
            return jsonify({
                "status": "error",
                "message": "No question provided"
            }), 400

        print(f"User question: {user_question}")

        # Step 1: Capture screenshot and extract code
        print("Step 1: Capturing screenshot and running OCR...")
        code_text = ocr_service.capture_and_ocr()

        # Check for OCR errors
        if not code_text:
            error_response = "I couldn't read your screen. Make sure there's code visible."
            send_to_pi(error_response)
            return jsonify({
                "status": "error",
                "message": "OCR returned empty result"
            }), 500

        if code_text.startswith("Could not capture screen"):
            error_response = "I couldn't capture your screen. Something went wrong."
            send_to_pi(error_response)
            return jsonify({
                "status": "error",
                "message": code_text
            }), 500

        if code_text == "No code detected":
            error_response = "I don't see any code on your screen. Can you make sure your code editor is visible?"
            send_to_pi(error_response)
            return jsonify({
                "status": "error",
                "message": "No text found on screen"
            }), 400

        # Step 2: Get contextual help from LLM
        if not llm_router:
            error_response = "My AI brain isn't working. Check the API key."
            send_to_pi(error_response)
            return jsonify({
                "status": "error",
                "message": "LLMRouter not initialized"
            }), 500

        print("Step 2: Getting contextual help from LLM...")
        answer = llm_router.get_contextual_help(code_text, user_question)
        print(f"LLM response: {answer}")

        # Step 3: Send answer to Pi
        print("Step 3: Sending response to Pi...")
        send_to_pi(answer)

        return jsonify({
            "status": "success",
            "question": user_question,
            "response": answer
        }), 200

    except Exception as e:
        error_msg = f"Error processing contextual help: {str(e)}"
        print(f"ERROR: {error_msg}")
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 500


@app.route('/status', methods=['GET'])
def status():
    """
    Health check endpoint to verify the server is running
    """
    return jsonify({
        "status": "running",
        "service": "Debug Duck Laptop Client",
        "port": LAPTOP_PORT,
        "llm_router": "initialized" if llm_router else "failed"
    }), 200


def speak_local(text):
    """
    Speak text on laptop speakers using pyttsx3

    Args:
        text (str): Text to speak

    Returns:
        bool: True if successful, False otherwise
    """
    if not tts_engine:
        print("ERROR: TTS engine not initialized")
        return False

    try:
        print(f"Speaking on laptop: '{text[:50]}...'")
        tts_engine.say(text)
        tts_engine.runAndWait()
        return True
    except Exception as e:
        print(f"ERROR speaking: {e}")
        return False


def send_to_pi(text):
    """
    Sends text to the Raspberry Pi to be spoken by the duck.

    Args:
        text (str): The text for the duck to speak

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.post(
            PI_URL,
            json={"text": text},
            timeout=35  # Increased to allow for TTS generation and playback
        )
        if response.status_code == 200:
            print(f"Successfully sent to Pi: '{text[:50]}...'")
            return True
        else:
            print(f"Pi returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to Pi at {PI_URL}")
        print("Make sure the Pi server is running and reachable")
        return False
    except requests.exceptions.Timeout:
        print("ERROR: Request to Pi timed out")
        return False
    except Exception as e:
        print(f"ERROR sending to Pi: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DEBUG DUCK - LAPTOP CLIENT SERVER")
    print("=" * 60)
    print(f"Starting Flask server on port {LAPTOP_PORT}...")
    print(f"Pi URL configured as: {PI_URL}")
    print("=" * 60 + "\n")

    # Run the Flask app
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=LAPTOP_PORT,
        debug=True
    )
