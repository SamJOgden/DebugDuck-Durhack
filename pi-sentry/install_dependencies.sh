#!/bin/bash
# Debug Duck Pi-Sentry - System Dependencies Installer
# Run this script with sudo to install all required system packages

set -e  # Exit on error

echo "======================================"
echo "Installing System Dependencies"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script needs to be run as root (sudo)"
    echo "Please run: sudo bash install_dependencies.sh"
    exit 1
fi

echo "Updating package list..."
apt update

echo ""
echo "Installing Python and build tools..."
apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    wget \
    curl

echo ""
echo "Installing OpenCV and computer vision libraries..."
apt install -y \
    python3-opencv \
    python3-numpy \
    libopencv-dev

echo ""
echo "Installing Flask and web framework..."
apt install -y \
    python3-flask \
    python3-requests

echo ""
echo "Installing GPIO libraries..."
apt install -y \
    python3-rpi.gpio \
    python3-lgpio

echo ""
echo "Installing Pygame (for GUI)..."
apt install -y \
    python3-pygame

echo ""
echo "Installing python-dotenv..."
apt install -y \
    python3-dotenv

echo ""
echo "Installing audio tools..."
apt install -y \
    alsa-utils \
    espeak \
    pulseaudio

echo ""
echo "Installing TensorFlow Lite dependencies..."
apt install -y \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz0b \
    libwebp7 \
    libjasper1 \
    libilmbase25 \
    libopenexr25 \
    libgstreamer1.0-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev

echo ""
echo "======================================"
echo "✅ System dependencies installed!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Install Python packages: pip3 install -r requirements.txt --break-system-packages"
echo "2. Build libcamera and picamera2 (see SSH_COMMANDS.md Phase 1)"
echo "3. Run setup script: bash setup_pi.sh"
echo ""
