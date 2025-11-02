# Debug Duck - Next Session Plan

## Current Status (End of Day 1)

### ✅ Completed
- **Laptop Client:** Fully built and tested
  - Flask server running on port 5001
  - OCR service with enhanced error handling
  - LLM integration with OpenRouter
  - All files created and working

- **Pi Sentry Files:** All created on Windows machine
  - Core application files (main.py, sentry_server.py, etc.)
  - Service files (fer_service.py, tts_service.py, etc.)
  - Test files updated for picamera2
  - Setup scripts (setup_pi.sh, install_dependencies.sh)
  - Documentation (README.md, SSH_COMMANDS.md, CAMERA_FIX.md)

- **Raspberry Pi:**
  - libcamera built from source ✅
  - picamera2 installed ✅
  - Camera working with test_fer.py ✅
  - TFLite import fixed (using tensorflow.lite)
  - Most dependencies installed
  - .env file exists with API key

### ⏳ Remaining Tasks
1. Transfer new files from Windows to Raspberry Pi
2. Update existing test_fer.py with the color fix
3. Install remaining Python dependencies
4. Set up Piper TTS
5. Test all individual components
6. Configure laptop IP in Pi's .env
7. Test full integration (laptop ↔ Pi)
8. Set up button GPIO
9. Test complete workflow

---

## Session Plan for Tomorrow

### Phase 1: File Transfer (15 minutes)

#### Files to Transfer to Raspberry Pi

**Location on Windows:** `C:\Users\soggy\Documents\debug-duck\pi-sentry\`

**Files to transfer:**
```
Core Application:
- main.py
- sentry_server.py
- fer_service.py
- tts_service.py
- duck_gui.py
- button_listener.py
- llm_router.py

Setup Files:
- requirements.txt
- setup_pi.sh
- install_dependencies.sh

Documentation:
- README.md
- SSH_COMMANDS.md
- CAMERA_FIX.md

Test Files (updated versions):
- test_fer_picamera2.py (new file with picamera2 support)
```

**Files already on Pi (don't overwrite):**
- `.env` (already configured)
- `test_fer.py` (already updated with picamera2 + color fix)
- `test_llm.py`
- `test_gui.py`
- `test_tts.py`
- `haarcascade_frontalface_default.xml` (if exists)

#### Transfer Methods

**Option 1: SCP (Recommended)**
```bash
# From Windows (PowerShell or Git Bash)
cd C:\Users\soggy\Documents\debug-duck\pi-sentry

# Transfer all Python files
scp *.py sjogden-durhack@raspberrypi.local:~/pi-sentry/

# Transfer shell scripts
scp *.sh sjogden-durhack@raspberrypi.local:~/pi-sentry/

# Transfer markdown docs
scp *.md sjogden-durhack@raspberrypi.local:~/pi-sentry/

# Transfer requirements
scp requirements.txt sjogden-durhack@raspberrypi.local:~/pi-sentry/
```

**Option 2: Git (Alternative)**
```bash
# Initialize git repo on Windows
cd C:\Users\soggy\Documents\debug-duck
git init
git add .
git commit -m "Complete pi-sentry implementation"

# Push to GitHub
git remote add origin <your-repo-url>
git push -u origin main

# Pull on Pi
ssh sjogden-durhack@raspberrypi.local
cd ~/debug-duck
git pull origin main
```

**Option 3: USB Drive**
- Copy pi-sentry folder to USB drive
- Plug into Pi
- Copy files: `cp /media/usb/pi-sentry/* ~/pi-sentry/`

---

### Phase 2: Apply the Color Fix to test_fer.py (5 minutes)

The test_fer.py on Pi needs one more update to match the fix we discussed:

**SSH into Pi and edit test_fer.py:**
```bash
ssh sjogden-durhack@raspberrypi.local
cd ~/pi-sentry
nano test_fer.py
```

**Find this section (around line 65-75):**
```python
for (x, y, w, h) in faces:
    face_roi_gray = gray_frame[y:y+h, x:x+w]

    # --- Preprocess for FER Model ---
    roi_resized = cv2.resize(face_roi_gray, (IMG_WIDTH, IMG_HEIGHT))
    roi_normalized = roi_resized.astype('float32') / 255.0
    roi_final = np.expand_dims(roi_normalized, axis=0)
    roi_final = np.expand_dims(roi_final, axis=-1)
```

**Replace with:**
```python
for (x, y, w, h) in faces:
    # Extract face from BGR frame (color, not grayscale!)
    face_roi_bgr = frame[y:y+h, x:x+w]

    # --- Preprocess for FER Model ---
    roi_resized = cv2.resize(face_roi_bgr, (IMG_WIDTH, IMG_HEIGHT))
    roi_normalized = roi_resized.astype('float32') / 255.0
    roi_final = np.expand_dims(roi_normalized, axis=0)
    # Note: No second expand_dims needed for color images
```

Save and test:
```bash
python3 test_fer.py
```

Should now detect emotions without errors! ✅

---

### Phase 3: Install Dependencies (10 minutes)

**On Raspberry Pi:**

```bash
cd ~/pi-sentry

# Activate venv if using one
source venv/bin/activate

# Install Python packages
pip3 install -r requirements.txt --break-system-packages

# Run setup script (downloads Piper TTS)
bash setup_pi.sh

# Make scripts executable
chmod +x install_dependencies.sh
chmod +x setup_pi.sh
```

**Check installations:**
```bash
# Verify key packages
python3 -c "import flask; print('Flask OK')"
python3 -c "import cv2; print('OpenCV OK')"
python3 -c "import tensorflow; print('TensorFlow OK')"
python3 -c "from picamera2 import Picamera2; print('Picamera2 OK')"
python3 -c "import RPi.GPIO as GPIO; print('GPIO OK')"
python3 -c "import pygame; print('Pygame OK')"

# Check if Piper is installed
ls -la piper/piper
```

---

### Phase 4: Configure Environment (5 minutes)

**Update .env file with laptop IP:**

```bash
cd ~/pi-sentry
nano .env
```

**Find your laptop's IP address:**

From Windows:
```powershell
ipconfig
# Look for IPv4 Address under your WiFi/Ethernet adapter
# Example: 192.168.1.100
```

**Update in .env:**
```bash
LAPTOP_CLIENT_URL="http://192.168.1.100:5001/get-help"
```

Replace `192.168.1.100` with your actual laptop IP.

**Verify both devices on same network:**
```bash
# From Pi, ping laptop
ping 192.168.1.100

# Should get responses
```

---

### Phase 5: Test Individual Components (15 minutes)

**Run each test to verify components work:**

```bash
cd ~/pi-sentry

# Test 1: TTS (Text-to-Speech)
python3 test_tts.py
# Expected: Should hear duck speak test phrases

# Test 2: GUI (Display)
python3 test_gui.py
# Expected: Duck image appears on touchscreen
# Press 'q' or tap screen to exit

# Test 3: LLM (AI Integration)
python3 test_llm.py
# Expected: Gets response from OpenRouter AI

# Test 4: FER (Facial Emotion Recognition)
python3 test_fer.py
# Expected: Camera starts, detects faces, prints emotions
# Make different facial expressions to test

# Test 5: Individual services
python3 tts_service.py
# Expected: Runs TTS tests

python3 fer_service.py
# Expected: Starts FER monitoring in background

python3 duck_gui.py
# Expected: GUI with emotion state changes

python3 button_listener.py
# Expected: Waits for button press (test with button or skip for now)
```

**Troubleshooting Quick Reference:**

| Error | Solution |
|-------|----------|
| `No module named 'X'` | `pip3 install X --break-system-packages` |
| Piper not found | `bash setup_pi.sh` |
| Audio not working | `alsamixer` to check volume |
| GPIO permission denied | `sudo python3 ...` or add user to gpio group |
| Camera error | Check `raspi-config` → Interface → Camera enabled |

---

### Phase 6: Test Flask Endpoints (10 minutes)

**Start the Pi sentry server:**
```bash
cd ~/pi-sentry
python3 sentry_server.py
```

**From another SSH session or laptop, test endpoints:**

```bash
# Test status endpoint
curl http://raspberrypi.local:5000/status

# Expected response:
# {
#   "status": "running",
#   "service": "Debug Duck Pi-Sentry",
#   "llm_router": "initialized",
#   "gui": "not set"
# }

# Test speak endpoint
curl -X POST http://raspberrypi.local:5000/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from the Debug Duck!"}'

# Expected: Duck should speak the text

# Test empathy endpoint
curl http://raspberrypi.local:5000/trigger-empathy

# Expected: Duck speaks a comforting phrase from AI
```

---

### Phase 7: Test Laptop → Pi Integration (10 minutes)

**Ensure laptop client is running:**

From Windows:
```bash
cd C:\Users\soggy\Documents\debug-duck\laptop-client
python client_server.py
```

**Test help request from Pi:**

From Pi SSH:
```bash
# Test that Pi can reach laptop
curl http://YOUR_LAPTOP_IP:5001/status

# Expected: Status response from laptop

# Simulate button press (triggers laptop)
curl http://YOUR_LAPTOP_IP:5001/get-help

# Expected:
# 1. Laptop captures screenshot
# 2. Laptop runs OCR
# 3. Laptop gets AI help
# 4. Laptop sends response to Pi
# 5. Pi speaks the response
```

**Check laptop server logs:** Should show:
```
HELP REQUEST RECEIVED from Pi
Step 1: Capturing screenshot and running OCR...
OCR extracted X characters
Step 2: Getting coding help from LLM...
Step 3: Sending response to Pi...
SUCCESS: Response sent to Pi
```

---

### Phase 8: Set Up GPIO Button (10 minutes)

**Physical wiring:**
- DFR0029 VCC → GPIO Pin 1 (3.3V)
- DFR0029 GND → GPIO Pin 6 (GND)
- DFR0029 Signal → GPIO Pin 11 (GPIO 17)

**Test button listener:**
```bash
cd ~/pi-sentry

# Run with sudo for GPIO access
sudo python3 button_listener.py

# Press the physical button
# Expected: See "BUTTON PRESSED!" and help request sent to laptop
```

**If "permission denied" error:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio sjogden-durhack

# Log out and back in
exit
ssh sjogden-durhack@raspberrypi.local

# Try without sudo
python3 button_listener.py
```

---

### Phase 9: Run Full Integration (15 minutes)

**Start all services together:**

```bash
cd ~/pi-sentry

# Run main application (with sudo for GPIO)
sudo python3 main.py
```

**Expected startup sequence:**
```
============================================================
DEBUG DUCK - MAIN APPLICATION
============================================================
Starting services...

[1/4] Starting Duck GUI...
✅ Duck GUI started

[2/4] Starting FER Service...
✅ FER Service started

[3/4] Starting Button Listener...
✅ Button Listener started

[4/4] Starting Flask Server...
✅ Flask Server started

============================================================
✅ ALL SERVICES STARTED
============================================================
Flask server running on http://0.0.0.0:5000
GUI displaying on touchscreen
FER monitoring active
Button listener active

Debug Duck is ready! 🦆
============================================================
```

**Test full workflows:**

**Workflow 1: Empathy Detection**
1. Make frustrated faces at camera
2. Wait for FER to detect frustration (~10 seconds)
3. Duck should speak comforting phrase
4. GUI should change emotions

**Workflow 2: Button Help Request**
1. Open code on laptop screen
2. Press physical button on Pi
3. Laptop captures screenshot, runs OCR
4. Laptop sends AI help to Pi
5. Duck speaks the coding advice

---

### Phase 10: Final Checks & Debugging (20 minutes)

**Verify all features:**

- [ ] GUI displays on touchscreen
- [ ] Duck image visible and centered
- [ ] FER detects faces and emotions
- [ ] Frustration triggers empathy response
- [ ] Duck speaks comforting phrases
- [ ] Button press triggers laptop
- [ ] Laptop OCR captures screen
- [ ] Laptop sends response to Pi
- [ ] Pi speaks AI's coding advice
- [ ] GUI changes emotions appropriately
- [ ] All services start without errors

**Common issues and fixes:**

| Issue | Fix |
|-------|-----|
| Services crash on startup | Check logs, install missing dependencies |
| Can't connect to laptop | Verify IP in .env, check network |
| No audio | Check speaker connection, run `alsamixer` |
| GUI not showing | Check framebuffer settings, try window mode |
| FER too slow | Increase `FER_FRAME_SKIP` in .env |
| Button not working | Check wiring, GPIO permissions |

**Check logs:**
```bash
# If main.py crashes, check what happened
python3 main.py 2>&1 | tee debug.log

# View recent system errors
journalctl -xe
```

---

### Phase 11: Optional Improvements (If Time)

**Performance tuning:**
```bash
# Edit .env for better performance
nano .env

# Adjust these values:
FER_FRAME_SKIP=3          # Process every 3rd frame (faster)
FER_FRUSTRATION_THRESHOLD=150  # Require more frames before trigger
```

**Add different duck emotions:**
```bash
# Create different duck images
# Place in assets/animations/:
# - duck_neutral.png
# - duck_concerned.png
# - duck_listening.png
# - duck_happy.png
```

**Set up auto-start on boot:**
```bash
# Create systemd service
sudo nano /etc/systemd/system/debug-duck.service

# Add:
[Unit]
Description=Debug Duck
After=network.target

[Service]
ExecStart=/home/sjogden-durhack/pi-sentry/venv/bin/python /home/sjogden-durhack/pi-sentry/main.py
WorkingDirectory=/home/sjogden-durhack/pi-sentry
User=sjogden-durhack
Restart=always

[Install]
WantedBy=multi-user.target

# Enable:
sudo systemctl enable debug-duck
sudo systemctl start debug-duck
```

---

## Quick Start Commands Summary

### Morning Setup Checklist
```bash
# 1. Transfer files (from Windows)
scp pi-sentry/*.py sjogden-durhack@raspberrypi.local:~/pi-sentry/

# 2. SSH to Pi
ssh sjogden-durhack@raspberrypi.local
cd ~/pi-sentry

# 3. Install dependencies
pip3 install -r requirements.txt --break-system-packages
bash setup_pi.sh

# 4. Configure laptop IP
nano .env  # Update LAPTOP_CLIENT_URL

# 5. Test individual components
python3 test_fer.py
python3 test_tts.py
python3 test_gui.py
python3 test_llm.py

# 6. Start laptop client (from Windows)
cd C:\Users\soggy\Documents\debug-duck\laptop-client
python client_server.py

# 7. Run full app (on Pi)
sudo python3 main.py
```

---

## Expected Final Result

When everything is working:

1. **Laptop Client** running on port 5001
2. **Pi Sentry** running all services
3. **Duck GUI** showing on touchscreen
4. **FER** monitoring facial emotions
5. **Button** connected and responsive
6. **Integration** working end-to-end:
   - Frustrated face → Duck speaks comfort
   - Button press → Laptop OCR → AI help → Duck speaks

---

## Files Location Reference

**Windows Machine:**
```
C:\Users\soggy\Documents\debug-duck\
├── laptop-client\          (✅ Complete & Running)
│   ├── client_server.py
│   ├── ocr_service.py
│   ├── llm_router.py
│   └── .env
│
└── pi-sentry\              (📦 Ready to transfer)
    ├── main.py
    ├── sentry_server.py
    ├── fer_service.py
    ├── tts_service.py
    ├── duck_gui.py
    ├── button_listener.py
    ├── llm_router.py
    ├── requirements.txt
    └── setup_pi.sh
```

**Raspberry Pi:**
```
/home/sjogden-durhack/
├── pi-sentry\              (🔄 Update with new files)
│   ├── test_fer.py         (✅ Working with picamera2)
│   ├── test_llm.py         (✅ Exists)
│   ├── test_gui.py         (✅ Exists)
│   ├── test_tts.py         (✅ Exists)
│   ├── .env                (✅ Exists - needs laptop IP)
│   ├── haarcascade_frontalface_default.xml
│   └── venv/               (✅ Active)
│
└── assets/
    └── emotion-model.tflite
```

---

## Success Criteria

✅ **Project is complete when:**
1. All services start without errors
2. FER detects emotions and triggers empathy
3. Button press triggers laptop help request
4. Laptop OCR captures code and gets AI help
5. Pi receives and speaks the AI response
6. GUI changes emotions appropriately
7. All interactions work smoothly

---

## Notes for Next Session

- **Camera is working!** ✅ (picamera2 successfully installed)
- **Color fix needed:** Update test_fer.py to use BGR instead of grayscale
- **Main blocker:** File transfer from Windows to Pi
- **Laptop client:** Already running and tested
- **Time estimate:** 2-3 hours for full integration testing

Good luck tomorrow! 🦆
