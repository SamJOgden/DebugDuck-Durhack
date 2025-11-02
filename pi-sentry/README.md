# Debug Duck - Pi Sentry

The Raspberry Pi component of the Debug Duck project. Acts as an empathetic companion that:
- Monitors your facial emotions and provides comfort when you're frustrated
- Listens for button presses to request coding help from the laptop client
- Displays an animated duck on a 7" touchscreen
- Speaks responses using text-to-speech

## Architecture

The Pi-Sentry consists of multiple integrated services:

- **Flask Server** (`sentry_server.py`) - Handles empathy triggers and speaking requests
- **FER Service** (`fer_service.py`) - Monitors facial emotions with picamera2
- **Button Listener** (`button_listener.py`) - Detects button presses via GPIO
- **Duck GUI** (`duck_gui.py`) - Displays animated duck on touchscreen
- **TTS Service** (`tts_service.py`) - Converts text to speech using Piper
- **LLM Router** (`llm_router.py`) - Gets comforting phrases from AI

## Hardware Requirements

- Raspberry Pi (3/4/5 with ARM64)
- Raspberry Pi Camera Module
- 7" Touchscreen Display
- DFR0029 Push Button Module
- Anker Soundcore Speaker (3.5mm audio)
- SD Card with Debian 13 (Trixie) or Raspberry Pi OS

## Quick Start

### 1. Fix Camera (libcamera Build)

The camera needs to be built from source on Debian 13. See [SSH_COMMANDS.md](SSH_COMMANDS.md) for detailed instructions.

**Quick fix for immediate error:**

```bash
# Install missing Python dependencies
pip3 install ply pybind11 jinja2 pyyaml --break-system-packages

# Retry libcamera build
cd ~/libcamera
rm -rf build
meson setup build
ninja -C build
sudo ninja -C build install
```

Then continue with the full camera setup in SSH_COMMANDS.md Phase 1.

### 2. Install System Dependencies

```bash
cd ~/pi-sentry
sudo bash install_dependencies.sh
```

### 3. Install Python Packages

```bash
pip3 install -r requirements.txt --break-system-packages
```

### 4. Set Up Piper TTS and Assets

```bash
bash setup_pi.sh
```

### 5. Configure Environment

Edit `.env` file and update:
- `LAPTOP_CLIENT_URL` - Replace `YOUR_LAPTOP_IP` with your laptop's actual IP address

```bash
nano .env
```

### 6. Test Individual Components

```bash
# Test TTS
python3 test_tts.py

# Test GUI
python3 test_gui.py

# Test LLM
python3 test_llm.py

# Test Camera + FER
python3 test_fer_picamera2.py
```

### 7. Run the Full Application

```bash
# Run with sudo for GPIO access
sudo python3 main.py
```

Or add your user to the gpio group:

```bash
sudo usermod -a -G gpio $USER
# Log out and log back in, then:
python3 main.py
```

## Project Structure

```
pi-sentry/
├── main.py                          # Main application orchestrator
├── sentry_server.py                 # Flask server
├── fer_service.py                   # Facial emotion recognition
├── button_listener.py               # GPIO button handler
├── duck_gui.py                      # Pygame GUI display
├── tts_service.py                   # Piper TTS wrapper
├── llm_router.py                    # OpenRouter integration
│
├── test_fer_picamera2.py            # Updated FER test with picamera2
├── test_fer.py                      # Original FER test (cv2.VideoCapture)
├── test_gui.py                      # GUI test
├── test_llm.py                      # LLM test
├── test_tts.py                      # TTS test
│
├── requirements.txt                 # Python dependencies
├── .env                             # Environment configuration
├── setup_pi.sh                      # Setup script (Piper TTS)
├── install_dependencies.sh          # System package installer
├── SSH_COMMANDS.md                  # Detailed SSH commands
└── README.md                        # This file
```

## Configuration

All configuration is in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | - | Your OpenRouter API key |
| `LAPTOP_CLIENT_URL` | - | Laptop client endpoint (update IP!) |
| `PI_HOST` | 0.0.0.0 | Flask server host |
| `PI_PORT` | 5000 | Flask server port |
| `FER_FRUSTRATION_THRESHOLD` | 100 | Frames of frustration before trigger |
| `FER_FRAME_SKIP` | 2 | Process every Nth frame |
| `FER_CONFIDENCE_THRESHOLD` | 0.5 | Minimum emotion confidence |
| `BUTTON_GPIO_PIN` | 17 | GPIO pin for button |
| `BUTTON_DEBOUNCE_TIME` | 1.0 | Button debounce seconds |

## Hardware Setup

### Camera Connection
1. Connect ribbon cable to CSI port
2. Enable camera: `sudo raspi-config` → Interface Options → Camera → Enable
3. Test: `libcamera-hello --list-cameras`

### Button Wiring (DFR0029)
- VCC → GPIO Pin 1 (3.3V)
- GND → GPIO Pin 6 (GND)
- Signal → GPIO Pin 11 (GPIO 17)

### Audio Output
- Plug speaker into 3.5mm audio jack
- Test: `speaker-test -t wav -c 2 -l 1`
- Adjust volume: `alsamixer`

## API Endpoints

### GET `/trigger-empathy`
Triggered when FER detects frustration.

**Response:**
```json
{
  "status": "success",
  "phrase": "Hey, take a breath. You've got this!"
}
```

### POST `/speak`
Receives text from laptop to speak.

**Request:**
```json
{
  "text": "I see your code. The bug is on line 42."
}
```

**Response:**
```json
{
  "status": "success",
  "text": "..."
}
```

### POST `/emotion`
Manually set duck emotion (testing).

**Request:**
```json
{
  "emotion": "happy"
}
```

### GET `/status`
Health check.

**Response:**
```json
{
  "status": "running",
  "service": "Debug Duck Pi-Sentry",
  "port": 5000,
  "llm_router": "initialized",
  "gui": "initialized"
}
```

## Workflow

### Phase 1: Empathetic Sentry
1. FER Service monitors facial emotions via camera
2. When frustration detected for 100+ frames:
   - Calls `/trigger-empathy` endpoint
   - LLM generates comforting phrase
   - GUI changes to "concerned"
   - Duck speaks phrase
   - GUI returns to "neutral"

### Phase 2: Coding Helper
1. User presses physical button
2. Button Listener detects press
3. Sends request to laptop client: `http://LAPTOP_IP:5001/get-help`
4. Laptop captures screenshot, runs OCR, gets AI help
5. Laptop sends response to Pi: `http://raspberrypi.local:5000/speak`
6. GUI changes to "listening"
7. Duck speaks the AI's advice
8. GUI returns to "neutral"

## Troubleshooting

### Camera Issues

**"Could not find Picamera2"**
- Complete libcamera build: See SSH_COMMANDS.md Phase 1
- Verify: `python3 -c "from picamera2 import Picamera2"`

**Camera shows black screen**
- Check ribbon cable connection
- Test: `libcamera-still -o test.jpg`
- Enable camera in raspi-config

### TTS Issues

**No sound**
- Check volume: `alsamixer`
- Test audio: `speaker-test -t wav -c 2 -l 1`
- Verify speaker connection

**Piper not found**
- Run: `bash setup_pi.sh`
- Check: `ls -la piper/piper`
- Make executable: `chmod +x piper/piper`

### GPIO Issues

**Button not responding**
- Check wiring (GPIO 17, 3.3V, GND)
- Run as sudo or add user to gpio group
- Test with: `python3 button_listener.py`

### Network Issues

**Can't reach laptop**
- Verify laptop IP in `.env`
- Check both on same network
- Test: `ping YOUR_LAPTOP_IP`
- Ensure laptop server is running

## Development

### Run Individual Services

```bash
# Server only
python3 sentry_server.py

# FER only
python3 fer_service.py

# GUI only
python3 duck_gui.py

# Button only
python3 button_listener.py
```

### Debug Logging

Set logging level in code:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Testing Without Hardware

- FER: Comment out picamera2 initialization
- Button: Use keyboard input instead of GPIO
- TTS: Print text instead of speaking
- GUI: Run in windowed mode on desktop

## Performance Tips

1. **Reduce FER load**: Increase `FER_FRAME_SKIP` to process fewer frames
2. **Lower FER sensitivity**: Increase `FER_FRUSTRATION_THRESHOLD`
3. **Optimize camera**: Use lower resolution in `fer_service.py`
4. **Reduce GUI FPS**: Lower frame rate in `duck_gui.py`

## Known Issues

1. **Debian 13 (Trixie) camera compatibility**: Requires building libcamera from source
2. **GPIO permissions**: May need sudo or gpio group membership
3. **First run slow**: Models and libraries load slowly initially
4. **Audio delay**: Piper TTS has ~1-2 second latency

## Next Steps

- [ ] Add different duck animations for each emotion
- [ ] Implement voice input (Phase 3) for questions
- [ ] Add configuration UI on touchscreen
- [ ] Create systemd service for auto-start
- [ ] Add data logging and analytics
- [ ] Implement emotion detection fine-tuning

## Resources

- [Piper TTS](https://github.com/rhasspy/piper)
- [libcamera Documentation](https://libcamera.org/getting-started.html)
- [picamera2 Documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [OpenRouter API](https://openrouter.ai/docs)

## License

MIT License - See LICENSE file for details

## Credits

Built for DurHack 2025 Hackathon 🦆
