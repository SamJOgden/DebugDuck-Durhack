import os

# Path to your piper executable (adjust if you put it elsewhere)
PIPER_PATH = "./piper/piper"
MODEL_PATH = "./piper/en_US-lessac-medium.onnx" # The voice file

def speak(text):
    print(f"Duck is saying: {text}")
    # Use os.system to build and run the command
    # This pipes the text to piper, which generates audio,
    # which is then piped to 'aplay' to be spoken.
    command = f'echo "{text}" | {PIPER_PATH} --model {MODEL_PATH} --output_file - | aplay'
    os.system(command)

# --- Let's test it ---
speak("Hello, this is a test of my voice.")
speak("One, two, three.")