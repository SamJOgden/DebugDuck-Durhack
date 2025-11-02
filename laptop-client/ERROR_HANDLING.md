# Error Handling & Logging Documentation

## Overview
Enhanced error handling and logging has been added to `ocr_service.py` and `client_server.py` for better debugging and user feedback.

## Error Messages

### OCR Service (`ocr_service.py`)

The OCR service now returns specific error messages for different failure scenarios:

| Error Condition | Return Value | Description |
|----------------|--------------|-------------|
| Tesseract not found | `"Could not capture screen - Tesseract OCR not found"` | Tesseract executable is missing |
| No monitor detected | `"Could not capture screen - No monitor detected"` | System has no display connected |
| Screenshot capture fails | `"Could not capture screen"` | mss failed to capture screenshot |
| Image conversion fails | `"Could not capture screen - Image conversion failed"` | PIL Image conversion error |
| OCR processing fails | `"Could not capture screen - OCR processing failed"` | Tesseract processing error |
| Empty OCR result | `"No code detected"` | Screenshot captured but no text found |
| Invalid region dimensions | `"Could not capture screen - Invalid region dimensions"` | Region width or height <= 0 |

## Logging Levels

### INFO Level
- Logs major steps in the process
- Success/failure outcomes
- Character counts from OCR

Example:
```
INFO - Starting screenshot capture and OCR process
INFO - Capturing screenshot...
INFO - Running OCR on screenshot...
INFO - OCR SUCCESS: Extracted 1115 characters
```

### DEBUG Level
- Detailed technical information
- Monitor dimensions
- Screenshot sizes
- Image conversion steps
- Tesseract command details

Example:
```
DEBUG - Monitor info: {'left': 0, 'top': 0, 'width': 2256, 'height': 1504}
DEBUG - Screenshot captured: size=Size(width=2256, height=1504)
DEBUG - Screenshot converted to PIL Image
```

### WARNING Level
- Non-critical issues
- Empty OCR results

Example:
```
WARNING - No code detected - Screen may be blank or contain only images
```

### ERROR Level
- All error conditions
- Includes detailed error messages
- Stack traces for unexpected errors

Example:
```
ERROR - Could not capture screen: Region capture failed - ...
ERROR - Could not capture screen - Tesseract OCR not found
```

## Client Server Error Handling (`client_server.py`)

### `/get-help` Endpoint

The endpoint now handles three distinct OCR error conditions:

#### 1. Empty Result
```json
{
  "status": "error",
  "message": "OCR returned empty result",
  "response": "I couldn't read your screen. Make sure there's code visible."
}
HTTP Status: 500
```

#### 2. Capture Failure
```json
{
  "status": "error",
  "message": "Could not capture screen - ...",
  "response": "I couldn't capture your screen. Something went wrong."
}
HTTP Status: 500
```

#### 3. No Code Detected
```json
{
  "status": "error",
  "message": "No text found on screen",
  "response": "I don't see any code on your screen. Can you make sure your code editor is visible?"
}
HTTP Status: 400
```

### Duck-Friendly Messages

All error responses sent to the Pi are phrased in a friendly, helpful tone:
- "I couldn't capture your screen. Something went wrong."
- "I don't see any code on your screen. Can you make sure your code editor is visible?"
- "My AI brain isn't working. Check the API key."

## Testing Error Handling

### Test OCR Service Directly
```bash
python ocr_service.py
```

This runs with DEBUG logging enabled and shows:
- All logging output
- Tesseract verification
- Screenshot capture process
- OCR extraction details
- Final result

### Test via Server Endpoint
```bash
# Start server
python client_server.py

# In another terminal, trigger help request
curl http://localhost:5001/get-help
```

## Debugging Tips

### Enable DEBUG Logging in Server
Add this to the top of `client_server.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**"Could not capture screen - Tesseract OCR not found"**
- Solution: Install Tesseract or update path in `ocr_service.py`
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

**"No code detected"**
- Solution: Ensure code editor is visible and contains readable text
- Check that text isn't too small or blurry
- Try maximizing your code editor window

**"Could not capture screen"**
- Check system permissions for screen capture
- Ensure display is properly connected
- Verify mss library is installed: `pip install mss`

## Logging Output Example

Full successful capture:
```
2025-11-02 01:52:37,692 - __main__ - INFO - TESTING OCR SERVICE
2025-11-02 01:52:37,692 - __main__ - INFO - Starting screenshot capture and OCR process
2025-11-02 01:52:37,692 - __main__ - INFO - Tesseract found at: C:\Program Files\Tesseract-OCR\tesseract.exe
2025-11-02 01:52:37,693 - __main__ - DEBUG - Initializing mss for screenshot capture
2025-11-02 01:52:37,841 - __main__ - DEBUG - Monitor info: {'left': 0, 'top': 0, 'width': 2256, 'height': 1504}
2025-11-02 01:52:37,841 - __main__ - INFO - Capturing screenshot...
2025-11-02 01:52:37,934 - __main__ - DEBUG - Screenshot captured: size=Size(width=2256, height=1504)
2025-11-02 01:52:37,956 - __main__ - DEBUG - Screenshot converted to PIL Image
2025-11-02 01:52:37,956 - __main__ - INFO - Running OCR on screenshot...
2025-11-02 01:52:41,945 - __main__ - DEBUG - OCR completed, extracted 1115 characters
2025-11-02 01:52:41,945 - __main__ - INFO - OCR SUCCESS: Extracted 1115 characters
```

## Benefits

1. **Better Debugging**: Detailed logs help identify exactly where failures occur
2. **User-Friendly**: Clear error messages help users understand what went wrong
3. **Monitoring**: Log levels allow different verbosity in development vs production
4. **Troubleshooting**: Specific error messages guide users to solutions
5. **Maintainability**: Consistent logging makes code easier to maintain
