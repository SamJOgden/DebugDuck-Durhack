import sounddevice as sd
import vosk
import json
import queue

# --- CONFIG ---
MODEL_PATH = "vosk-model-small-en-us-0.15" # The folder you just downloaded
DEVICE_INFO = sd.query_devices(kind='input')
SAMPLE_RATE = int(DEVICE_INFO['default_samplerate'])
# --------------

try:
    model = vosk.Model(MODEL_PATH)
    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    print("--- VOSK TEST ---")
    print("Please say something into your laptop mic...")
    
    # Start listening
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, 
                           device=None, dtype='int16', channels=1, callback=callback):
        
        rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result['text']:
                    print(f"Vosk heard you say: {result['text']}")
                    break # Stop after first successful phrase
            # else:
            #     print(json.loads(rec.PartialResult())) # Uncomment for partial results

except FileNotFoundError:
    print(f"Error: Could not find Vosk model.")
    print(f"Make sure the folder '{MODEL_PATH}' exists in your laptop-client directory.")
except Exception as e:
    print(f"An error occurred: {e}")
    print("Do you have a microphone connected?")