# Debug Duck - Laptop Client

This is the laptop client for the Debug Duck project. It runs a Flask server that listens for help requests from the Raspberry Pi, captures screenshots, performs OCR, and uses AI to provide coding help.

## Architecture

The laptop client consists of three main components:

1. **client_server.py** - Flask server running on port 5001
2. **ocr_service.py** - Screenshot capture and OCR using mss and pytesseract
3. **llm_router.py** - OpenRouter integration for AI-powered coding help

## Prerequisites

### 1. Install Tesseract OCR

Tesseract is required for OCR functionality.

**Windows:**
- Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR\`
- If installed elsewhere, update the path in `ocr_service.py`

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt install tesseract-ocr
```

### 2. Set up Python Environment

Make sure you're using Python 3.8 or higher.

## Installation

1. **Activate virtual environment** (if not already activated):
   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   - The `.env` file should already contain your `OPENROUTER_API_KEY`
   - If not, create a `.env` file with:
     ```
     OPENROUTER_API_KEY=your_api_key_here
     ```

## Running the Server

Start the Flask server:

```bash
python client_server.py
```

The server will:
- Listen on `http://0.0.0.0:5001` (accessible from the Pi)
- Wait for help requests from the Raspberry Pi
- Automatically capture screenshots, run OCR, and get AI help

## Testing

### Test Individual Components

**Test LLM Router:**
```bash
python llm_router.py
```

**Test OCR Service:**
```bash
python ocr_service.py
```

**Test Full OCR (existing test file):**
```bash
python test_laptop_ocr.py
```

### Test Server Endpoints

**Check server status:**
```bash
curl http://localhost:5001/status
```

**Trigger help request (simulates Pi button press):**
```bash
curl http://localhost:5001/get-help
```

## API Endpoints

### GET/POST `/get-help`
Triggered by the Pi when the button is pressed.
- Captures screenshot
- Runs OCR on code
- Gets AI analysis
- Sends response to Pi

**Response:**
```json
{
  "status": "success",
  "ocr_length": 1234,
  "response": "AI's coding advice...",
  "pi_status": "sent"
}
```

### POST `/get-contextual-help`
Phase 3 endpoint that includes both code and voice question.

**Request:**
```json
{
  "question": "Why am I getting a NoneType error?"
}
```

**Response:**
```json
{
  "status": "success",
  "question": "Why am I getting a NoneType error?",
  "response": "AI's answer..."
}
```

### GET `/status`
Health check endpoint.

**Response:**
```json
{
  "status": "running",
  "service": "Debug Duck Laptop Client",
  "port": 5001,
  "llm_router": "initialized"
}
```

## Configuration

### Change Pi URL
Edit `client_server.py`:
```python
PI_URL = "http://raspberrypi.local:5000/speak"  # Change this if needed
```

### Change Server Port
Edit `client_server.py`:
```python
LAPTOP_PORT = 5001  # Change this if needed
```

### Tesseract Path (Windows)
Edit `ocr_service.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Troubleshooting

### "Could not connect to Pi"
- Make sure the Pi server is running
- Check that `raspberrypi.local` resolves (try `ping raspberrypi.local`)
- Try using the Pi's IP address instead in `PI_URL`

### "Tesseract not found"
- Verify Tesseract is installed: `tesseract --version`
- Check the path in `ocr_service.py` matches your installation

### "OPENROUTER_API_KEY not set"
- Check that `.env` file exists in the laptop-client directory
- Verify the API key is correctly formatted in `.env`
- Make sure `python-dotenv` is installed

### OCR returns no text
- Ensure there's visible code on your screen
- Check that the text is clear and readable
- Try testing with `test_laptop_ocr.py` to see what OCR captures

## Development

### Project Structure
```
laptop-client/
├── client_server.py        # Main Flask server
├── ocr_service.py          # Screenshot + OCR
├── llm_router.py           # OpenRouter AI integration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API keys)
├── test_laptop_ocr.py      # OCR test script
└── test_laptop_stt.py      # Speech-to-text test script
```

### Adding Features
- For new endpoints, add routes to `client_server.py`
- For new AI models, add methods to `llm_router.py`
- For OCR improvements, modify `ocr_service.py`

## Phase Implementation

- **Phase 1**: Emotional support (runs on Pi)
- **Phase 2**: Code-only help (this client) ✅
- **Phase 3**: Code + voice question (requires STT integration)

For Phase 3, uncomment the STT dependencies in `requirements.txt` and integrate with `test_laptop_stt.py`.
