# Camera Fix for Debian 13 (Trixie)

## Issue
You're running Debian 13 (Trixie) which doesn't have pre-built picamera2 packages. You need to build libcamera and picamera2 from source.

## Current Error
```
meson.build:291:8: ERROR: Problem encountered: Python module 'ply' not found
```

## Quick Fix

Run these commands on your Raspberry Pi via SSH:

### Step 1: Install Missing Python Dependencies

```bash
# Install the required Python modules for the meson build
pip3 install ply pybind11 jinja2 pyyaml --break-system-packages
```

**Why `--break-system-packages`?**
Debian 13 uses PEP 668 which prevents pip from modifying system Python packages without this flag.

### Step 2: Clean and Rebuild libcamera

```bash
# Navigate to libcamera directory
cd ~/libcamera

# Remove the previous failed build
rm -rf build

# Configure the build
meson setup build

# Build libcamera (this will take 5-10 minutes)
ninja -C build

# Install libcamera system-wide
sudo ninja -C build install

# Update library cache
sudo ldconfig
```

### Step 3: Verify libcamera Installation

```bash
# Check if libcamera is installed
ldconfig -p | grep libcamera

# Test with libcamera tools
libcamera-hello --list-cameras
```

**Expected output:** You should see your camera listed.

### Step 4: Build Python Bindings

```bash
# Navigate to Python bindings directory
cd ~/libcamera/src/py

# Install Python bindings
pip3 install . --break-system-packages
```

### Step 5: Install picamera2

```bash
# Go to home directory
cd ~

# Clone picamera2 if not already done
if [ ! -d "picamera2" ]; then
    git clone https://github.com/raspberrypi/picamera2.git
fi

# Navigate to picamera2
cd picamera2

# Install picamera2
pip3 install . --break-system-packages
```

### Step 6: Test picamera2

```bash
# Test if picamera2 can be imported
python3 -c "from picamera2 import Picamera2; print('✅ Picamera2 installed successfully!')"
```

**Expected output:** `✅ Picamera2 installed successfully!`

### Step 7: Test Camera Capture

```bash
# Capture a test image
libcamera-still -o test.jpg

# Check if image was created
ls -lh test.jpg
```

### Step 8: Test FER with picamera2

```bash
# Navigate to pi-sentry directory
cd ~/pi-sentry

# Run the updated FER test
python3 test_fer_picamera2.py
```

**Expected:** Camera preview starts, faces are detected, emotions are printed to terminal.

---

## If Build Fails

### Missing Dependencies Error

If you get errors about missing libraries during the build, install additional dependencies:

```bash
sudo apt install -y \
    libboost-dev \
    libdrm-dev \
    libexif-dev \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavformat-dev \
    libswresample-dev \
    libswscale-dev \
    python3-numpy \
    python3-pyqt5
```

### Check Build Log

If meson setup fails, check the detailed log:

```bash
cat ~/libcamera/build/meson-logs/meson-log.txt
```

### Camera Not Detected

Enable camera in Raspberry Pi configuration:

```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Reboot: sudo reboot
```

Check camera connection:

```bash
# List video devices
v4l2-ctl --list-devices

# Or use libcamera
libcamera-hello --list-cameras
```

---

## Alternative: Try USB Webcam

If the Pi Camera build continues to fail, you can temporarily use a USB webcam:

1. Plug in USB webcam
2. Test with `libcamera-hello` or `v4l2-ctl --list-devices`
3. The existing `test_fer.py` (using cv2.VideoCapture) should work with USB cameras

---

## Next Steps After Camera Works

Once picamera2 is installed and working:

1. **Test FER:** `python3 test_fer_picamera2.py`
2. **Test all components:** Run all test files
3. **Launch full app:** `sudo python3 main.py`
4. **Configure laptop IP:** Update `LAPTOP_CLIENT_URL` in your existing `.env` file
5. **Test integration:** Press button → laptop processes → Pi speaks

---

## Progress Checklist

- [ ] Install Python dependencies (ply, pybind11, jinja2, pyyaml)
- [ ] Clean libcamera build directory
- [ ] Run meson setup build
- [ ] Run ninja -C build
- [ ] Install libcamera with sudo
- [ ] Build Python bindings
- [ ] Install picamera2
- [ ] Test picamera2 import
- [ ] Test camera capture
- [ ] Test FER with picamera2
- [ ] Update laptop IP in .env
- [ ] Launch main.py

---

## Support

- Full SSH commands: See `SSH_COMMANDS.md`
- General setup: See `README.md`
- Detailed troubleshooting: See `SSH_COMMANDS.md` Troubleshooting section

Good luck! 🦆
