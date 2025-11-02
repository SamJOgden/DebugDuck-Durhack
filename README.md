# 🦆 Debug Duck - Your Emotional Support Debug Assistant

An AI-powered debug companion built with Raspberry Pi 5 that provides emotional support and coding help during frustrating debugging sessions.

![Debug Duck Banner](assets/animations/duck_neutral.png)

## 🎯 What is Debug Duck?

Debug Duck is a physical AI assistant that:
- **Detects your frustration** using facial emotion recognition (FER)
- **Offers comfort** with AI-generated empathy responses
- **Provides coding help** by analyzing your screen when you press a button
- **Speaks naturally** using text-to-speech (Piper TTS)
- **Displays emotions** on a touchscreen with animated duck graphics

Built for DurHack 2024, this project combines computer vision, LLMs, OCR, and IoT to create a supportive coding companion.

---

## 🏗️ Architecture

### Two-Component System:

#### 1. **Laptop Client** (Windows/Mac/Linux)
- Captures screenshots
- Performs OCR (text extraction)
- Sends code to LLM (OpenRouter API)
- Communicates with Pi

#### 2. **Pi Sentry** (Raspberry Pi 5)
- Monitors emotions via camera (FER)
- Displays animated duck on touchscreen
- Listens for button presses
- Speaks AI responses via TTS
- Coordinates all services

### Communication Flow:
```
[Button Press] → [Pi] → [Laptop: Screenshot → OCR → LLM] → [Pi: TTS]
         ↓
[Frustrated Face] → [Pi: FER → LLM] → [Empathy Response]
```

---

## 🚀 Features

### Emotion Detection & Support
- Real-time facial emotion recognition using TensorFlow Lite
- Detects frustration/stress from facial expressions
- Generates personalized comfort messages using AI
- Responds with empathy when you need it most

### Coding Help on Demand
- Press physical button to trigger help request
- Laptop captures your screen and extracts code via OCR
- AI analyzes your code and provides debugging advice
- Duck speaks the advice out loud

### Natural Speech
- High-quality TTS using Piper voice models
- Speaks in a friendly, supportive tone
- Handles long AI responses gracefully

### Visual Feedback
- Animated duck graphics on 7" touchscreen
- Changes emotions based on context
- Pygame-based GUI with multiple emotion states

---

## 📦 Components

### Hardware Required
- **Raspberry Pi 5** (4GB+ RAM recommended)
- **Raspberry Pi Camera Module** (v2 or v3)
- **7" Touchscreen Display** (official or compatible)
- **Physical Button** (DFR0029 or similar)
- **Speaker/Audio Output** (USB or 3.5mm)
- **Laptop** (Windows/Mac/Linux)

### Software Stack
- **Python 3.13+**
- **TensorFlow Lite** (emotion recognition)
- **OpenCV & picamera2** (camera processing)
- **Pygame** (GUI display)
- **Piper TTS** (text-to-speech)
- **Flask** (API servers)
- **EasyOCR** (text extraction)
- **OpenRouter API** (LLM integration)

---

## 🛠️ Setup Instructions

### Prerequisites
1. OpenRouter API key (get from [openrouter.ai](https://openrouter.ai))
2. Both devices on same network
3. SSH access to Raspberry Pi

### Laptop Client Setup

```bash
cd laptop-client

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo 'OPENROUTER_API_KEY="your-api-key-here"' > .env
echo 'PI_SENTRY_URL="http://YOUR_PI_IP:5000/speak"' >> .env

# Run the server
python client_server.py
```

The laptop server will run on port 5001.

### Raspberry Pi Setup

```bash
cd pi-sentry

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup script (downloads Piper TTS)
bash setup_pi.sh

# Create .env file
echo 'OPENROUTER_API_KEY="your-api-key-here"' > .env
echo 'LAPTOP_CLIENT_URL="http://YOUR_LAPTOP_IP:5001/get-help"' >> .env

# Run the main application (requires sudo for GPIO)
sudo /home/YOUR_USERNAME/pi-sentry/venv/bin/python main.py
```

### Hardware Wiring
- **Camera**: Connect to Pi CSI port
- **Touchscreen**: Connect via DSI or HDMI
- **Button**:
  - VCC → Pin 1 (3.3V)
  - GND → Pin 6 (GND)
  - Signal → Pin 11 (GPIO 17)
- **Speaker**: USB or 3.5mm audio jack

---

## 📖 Usage

### Workflow 1: Emotion-Based Support
1. Start coding on your laptop
2. Pi camera continuously monitors your face
3. When frustration is detected (angry/sad expressions)
4. Duck speaks a comforting AI-generated message
5. GUI changes to show empathetic emotion

### Workflow 2: Button-Triggered Help
1. Encounter a bug in your code
2. Press the physical button on Pi
3. Laptop captures screenshot and extracts code via OCR
4. AI analyzes the code and provides debugging advice
5. Duck speaks the AI's suggestions
6. GUI updates to show "listening" state

### Manual Testing (Without Button)
```bash
# From Windows/Mac/Linux:
curl http://YOUR_LAPTOP_IP:5001/get-help

# Or trigger Pi directly:
curl http://YOUR_PI_IP:5000/trigger-empathy
```

---

## 🧪 Testing Individual Components

### Test Laptop Client
```bash
cd laptop-client
python client_server.py

# In another terminal:
curl http://localhost:5001/status
```

### Test Pi Components
```bash
cd pi-sentry
source venv/bin/activate

# Test GUI
python test_gui.py

# Test TTS
python test_tts.py

# Test FER (Facial Emotion Recognition)
python test_fer.py

# Test LLM
python test_llm.py
```

---

## 🔧 Configuration

### Environment Variables

**Laptop Client (.env):**
```bash
OPENROUTER_API_KEY="sk-or-v1-..."
PI_SENTRY_URL="http://10.249.14.247:5000/speak"
```

**Pi Sentry (.env):**
```bash
OPENROUTER_API_KEY="sk-or-v1-..."
LAPTOP_CLIENT_URL="http://10.249.8.196:5001/get-help"
BUTTON_GPIO_PIN=17
FER_FRAME_SKIP=2
FER_FRUSTRATION_THRESHOLD=100
```

### Adjustable Parameters
- `FER_FRAME_SKIP`: Process every Nth frame (higher = faster, less accurate)
- `FER_FRUSTRATION_THRESHOLD`: Frames of frustration before triggering
- `BUTTON_DEBOUNCE_TIME`: Seconds between button presses
- `DISPLAY`: Set to `:0` for SSH sessions with GUI

---

## 🐛 Troubleshooting

### "No module named 'tensorflow'"
```bash
# Make sure you're in the virtual environment
source venv/bin/activate
pip install tensorflow
```

### "Cannot determine SOC peripheral base address" (Pi 5)
This is a known issue with RPi.GPIO on Pi 5. The button won't work, but you can trigger help requests manually via curl.

### Duck doesn't appear on touchscreen
```bash
# Make sure DISPLAY is set
export DISPLAY=:0
python test_gui.py
```

### TTS timeout errors
Increase timeout in `.env`:
```bash
TTS_TIMEOUT=30
```

### Camera not detected
```bash
# Check camera connection
libcamera-hello

# Enable camera in raspi-config
sudo raspi-config
# Interface Options → Camera → Enable
```

---

## 📁 Project Structure

```
debug-duck/
├── laptop-client/           # Laptop-side code
│   ├── client_server.py    # Flask API server
│   ├── ocr_service.py      # Screenshot & OCR
│   ├── llm_router.py       # OpenRouter integration
│   └── requirements.txt
│
├── pi-sentry/              # Raspberry Pi code
│   ├── main.py             # Main orchestrator
│   ├── sentry_server.py    # Flask API server
│   ├── fer_service.py      # Emotion recognition
│   ├── tts_service.py      # Text-to-speech
│   ├── duck_gui.py         # Pygame GUI
│   ├── button_listener.py  # GPIO button handler
│   ├── llm_router.py       # AI integration
│   └── requirements.txt
│
├── assets/                 # Images & models
│   ├── animations/         # Duck emotion graphics
│   └── emotion-model.tflite
│
└── README.md
```

---

## 🎓 Technical Details

### Facial Emotion Recognition (FER)
- Model: Custom TFLite CNN trained on FER2013 dataset
- Input: 64x64 RGB images from camera
- Output: 7 emotions (angry, disgust, fear, happy, neutral, sad, surprise)
- Detects faces using Haar Cascade
- Processes every 2nd frame for performance

### LLM Integration
- Provider: OpenRouter API
- Model: Configurable (default: claude-3-sonnet)
- Context: Code extracted from screen + user frustration level
- Response: Concise debugging advice or empathy

### Text-to-Speech
- Engine: Piper (high-quality neural TTS)
- Voice: en_US-lessac-medium
- Output: Direct to audio device via aplay

---

## 🤝 Contributing

This project was built for DurHack 2024. Feel free to fork, modify, and improve!

### Ideas for Enhancement
- [ ] Support for multiple duck personalities
- [ ] Voice input for asking specific questions
- [ ] Integration with IDE plugins
- [ ] Cloud storage for debugging history
- [ ] Multi-language support
- [ ] GPIO support for Raspberry Pi 5 (gpiod library)

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **DurHack 2024** for the inspiration
- **OpenRouter** for LLM API access
- **Piper TTS** for high-quality speech synthesis
- **TensorFlow** for emotion recognition
- **Claude Code** for development assistance

---

## 📞 Contact

Built by Sam Ogden for DurHack 2024

- GitHub: [@SamJOgden](https://github.com/SamJOgden)
- Project: [DebugDuck-Durhack](https://github.com/SamJOgden/DebugDuck-Durhack)

---

**Made with ❤️ and 🦆 during DurHack 2024**

🤖 *Generated with [Claude Code](https://claude.com/claude-code)*
