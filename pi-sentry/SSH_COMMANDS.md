# SSH Commands for Debug Duck Pi Setup

This document contains all the commands you need to run on your Raspberry Pi via SSH to set up the Debug Duck system.

## Phase 1: Fix libcamera Build

### Step 1: Install Python Dependencies for Meson Build

The libcamera build failed because Python modules are missing. Install them:

```bash
# Install required Python packages for libcamera build
pip3 install ply pybind11 jinja2 pyyaml --break-system-packages
```

**Note:** The `--break-system-packages` flag is required on Debian 13 (Trixie) due to PEP 668.

### Step 2: Clean and Rebuild libcamera

```bash
# Navigate to libcamera directory
cd ~/libcamera

# Remove previous failed build
rm -rf build

# Configure build with meson
meson setup build

# Build libcamera (this will take several minutes)
ninja -C build

# Install libcamera system-wide
sudo ninja -C build install

# Update library cache
sudo ldconfig
```

**Expected output:** You should see "Installing..." messages and no errors.

### Step 3: Build Python Bindings for libcamera

```bash
# Navigate to Python bindings directory
cd ~/libcamera/src/py

# Install Python bindings
pip3 install . --break-system-packages
```

### Step 4: Install picamera2

```bash
# Navigate to home directory
cd ~

# Clone picamera2 repository (if not already cloned)
if [ ! -d "picamera2" ]; then
    git clone https://github.com/raspberrypi/picamera2.git
fi

cd picamera2

# Install picamera2
pip3 install . --break-system-packages
```

### Step 5: Test picamera2 Installation

```bash
# Test if picamera2 can be imported
python3 -c "from picamera2 import Picamera2; print('✅ Picamera2 installed successfully!')"
```

**Expected output:** `✅ Picamera2 installed successfully!`

If you see this message, the camera stack is ready! If you get an error, see the Troubleshooting section below.

---

## Phase 2: Install System Dependencies

### Install Required APT Packages

```bash
# Update package list
sudo apt update

# Install Python, OpenCV, GPIO, and other dependencies
sudo apt install -y \
    python3-pip \
    python3-opencv \
    python3-numpy \
    python3-flask \
    python3-dotenv \
    python3-rpi.gpio \
    python3-pygame \
    libtesseract-dev \
    espeak \
    alsa-utils \
    git \
    wget
```

### Install TFLite Runtime (for Emotion Recognition)

```bash
# Install TensorFlow Lite runtime
pip3 install tflite-runtime --break-system-packages
```

---

## Phase 3: Set Up Project Directory

### Clone/Update Debug Duck Repository

If you haven't already cloned the project:

```bash
cd ~
# You'll need to transfer files from your Windows machine
# or set up git repository
```

For now, we'll assume files are transferred via SCP or similar.

### Download Haar Cascade for Face Detection

```bash
# Navigate to pi-sentry directory
cd ~/pi-sentry

# Download Haar Cascade classifier
wget https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml
```

---

## Phase 4: Install Piper TTS

### Download and Set Up Piper TTS

```bash
# Navigate to pi-sentry directory
cd ~/pi-sentry

# Create piper directory
mkdir -p piper
cd piper

# Download Piper for ARM64 (Raspberry Pi)
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz

# Extract
tar -xzf piper_arm64.tar.gz

# Download voice model (en_US-lessac-medium)
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Make piper executable
chmod +x piper

# Test Piper
echo "Hello from Debug Duck!" | ./piper --model en_US-lessac-medium.onnx --output_file - | aplay
```

**Expected output:** You should hear "Hello from Debug Duck!" from your speaker.

---

## Phase 5: Install Python Packages

### Install Required Python Packages

```bash
# Navigate to pi-sentry directory
cd ~/pi-sentry

# Install packages from requirements.txt
pip3 install -r requirements.txt --break-system-packages
```

---

## Phase 6: Configure Environment Variables

### Create/Edit .env File

```bash
# Navigate to pi-sentry directory
cd ~/pi-sentry

# Create .env file with your API key
nano .env
```

Add this content (replace with your actual API key):
```
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
LAPTOP_CLIENT_URL=http://YOUR_LAPTOP_IP:5001/get-help
```

Save and exit (Ctrl+X, then Y, then Enter).

---

## Phase 7: Test Individual Components

### Test 1: GUI Display

```bash
cd ~/pi-sentry
python3 test_gui.py
```

**Expected:** Duck image appears on touchscreen. Press 'q' or tap screen to exit.

### Test 2: TTS (Text-to-Speech)

```bash
cd ~/pi-sentry
python3 test_tts.py
```

**Expected:** You hear the duck speak test phrases.

### Test 3: LLM Integration

```bash
cd ~/pi-sentry
python3 test_llm.py
```

**Expected:** You see a response from the AI (should say "Quack!").

### Test 4: FER (Facial Emotion Recognition) with picamera2

```bash
cd ~/pi-sentry
python3 test_fer_picamera2.py
```

**Expected:** Camera preview window opens, faces are detected, emotions are printed to terminal.

---

## Phase 8: Run Integrated Application

### Start the Debug Duck Sentry Server

```bash
cd ~/pi-sentry
python3 main.py
```

**Expected:** All services start, Flask server runs on port 5000, FER monitoring begins, GUI displays.

---

## Troubleshooting

### libcamera build fails
- Make sure all Python packages are installed: `pip3 list | grep -E "ply|pybind11|jinja2"`
- Check meson log: `cat ~/libcamera/build/meson-logs/meson-log.txt`

### "Can't import picamera2"
- Verify installation: `pip3 show picamera2`
- Check libcamera is installed: `ldconfig -p | grep libcamera`
- Ensure camera is enabled: `sudo raspi-config` → Interface Options → Camera → Enable

### Camera shows black screen
- Check camera connection (ribbon cable)
- Verify camera is detected: `libcamera-hello --list-cameras`
- Try: `libcamera-still -o test.jpg` (should capture an image)

### Piper TTS no sound
- Check volume: `alsamixer`
- Test audio: `speaker-test -t wav -c 2`
- Verify audio device: `aplay -l`

### GPIO button not responding
- Verify wiring (GPIO 17, 3.3V, GND)
- Check GPIO permissions: Add user to gpio group: `sudo usermod -a -G gpio $USER`
- Log out and log back in

### Flask server won't start
- Check if port 5000 is in use: `sudo lsof -i :5000`
- Kill existing process: `sudo kill -9 <PID>`

---

## Quick Reference

### Start Services Individually

```bash
# Start Flask server only
cd ~/pi-sentry
python3 sentry_server.py

# Start FER monitoring only
python3 fer_service.py

# Start GUI only
python3 duck_gui.py

# Start button listener only
python3 button_listener.py
```

### Stop Services

```bash
# Find Python processes
ps aux | grep python3

# Kill specific service
pkill -f sentry_server.py
pkill -f fer_service.py
pkill -f duck_gui.py
pkill -f button_listener.py
```

### Check Logs

```bash
# View recent errors
journalctl -xe

# Monitor system log
tail -f /var/log/syslog
```

---

## Next Steps After Setup

1. Test laptop-to-Pi communication: Press button → should trigger laptop OCR
2. Test Pi-to-laptop communication: Pi sends response back to speak
3. Test FER detection: Make frustrated face → duck should respond
4. Fine-tune emotion detection threshold if needed
5. Customize duck phrases in llm_router.py

**You're ready to demo Debug Duck at the hackathon! 🦆**
