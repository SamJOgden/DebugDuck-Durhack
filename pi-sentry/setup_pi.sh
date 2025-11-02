#!/bin/bash
# Debug Duck Pi-Sentry Setup Script
# Run this script to download and set up Piper TTS

set -e  # Exit on error

echo "======================================"
echo "Debug Duck Pi-Sentry Setup"
echo "======================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"
echo ""

# ===== Download Haar Cascade =====
echo "[1/4] Downloading Haar Cascade for face detection..."
if [ ! -f "haarcascade_frontalface_default.xml" ]; then
    wget https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml
    echo "✅ Haar Cascade downloaded"
else
    echo "✅ Haar Cascade already exists"
fi
echo ""

# ===== Download and Set Up Piper TTS =====
echo "[2/4] Setting up Piper TTS..."

# Create piper directory if it doesn't exist
mkdir -p piper
cd piper

# Download Piper for ARM64 if not already downloaded
if [ ! -f "piper" ]; then
    echo "Downloading Piper for ARM64..."
    wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz

    echo "Extracting Piper..."
    tar -xzf piper_arm64.tar.gz

    # Make piper executable
    chmod +x piper

    echo "✅ Piper downloaded and extracted"
else
    echo "✅ Piper already exists"
fi

# Download voice model if not already downloaded
if [ ! -f "en_US-lessac-medium.onnx" ]; then
    echo "Downloading voice model (en_US-lessac-medium)..."
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
    echo "✅ Voice model downloaded"
else
    echo "✅ Voice model already exists"
fi

cd ..
echo ""

# ===== Test Piper TTS =====
echo "[3/4] Testing Piper TTS..."
echo "Testing audio output..." | ./piper/piper --model piper/en_US-lessac-medium.onnx --output_file - | aplay 2>/dev/null || echo "⚠️  Audio test failed (this is okay if you don't have speakers connected)"
echo ""

# ===== Check .env File =====
echo "[4/4] Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "Please create .env file with your API key and laptop IP."
    echo "See .env file for template."
else
    echo "✅ .env file found"

    # Check if laptop IP is configured
    if grep -q "YOUR_LAPTOP_IP" .env; then
        echo "⚠️  WARNING: LAPTOP_CLIENT_URL not configured in .env"
        echo "Please edit .env and replace YOUR_LAPTOP_IP with your laptop's IP address"
    else
        echo "✅ Laptop client URL configured"
    fi
fi
echo ""

echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and set your laptop's IP address"
echo "2. Install Python dependencies: pip3 install -r requirements.txt --break-system-packages"
echo "3. Test individual components:"
echo "   - python3 test_tts.py (test TTS)"
echo "   - python3 test_gui.py (test GUI)"
echo "   - python3 test_llm.py (test LLM)"
echo "   - python3 test_fer_picamera2.py (test camera + FER)"
echo "4. Run the full application: python3 main.py"
echo ""
echo "For troubleshooting, see SSH_COMMANDS.md"
echo ""
