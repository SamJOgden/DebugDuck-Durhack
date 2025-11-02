import mss
import pytesseract
from PIL import Image

# --- IMPORTANT ---
# You must tell pytesseract where you installed Tesseract-OCR.
# Find the tesseract.exe file (usually here) and update this path:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def test_ocr():
    print("Attempting to take screenshot and run OCR...")
    try:
        with mss.mss() as sct:
            # Get the first monitor
            monitor = sct.monitors[1] 
            
            # Capture the screen
            sct_img = sct.grab(monitor)
            
            # Convert to a PIL Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            
            # Run OCR
            text = pytesseract.image_to_string(img)
            
            if text.strip():
                print("\n--- OCR SUCCESS! ---")
                print("Found the following text on your screen:")
                print(text[:500] + "...") # Print first 500 chars
            else:
                print("OCR ran, but found no text.")

    except Exception as e:
        print(f"\n--- OCR FAILED ---")
        print(f"Error: {e}")
        print("Did you update the 'tesseract_cmd' path in this script?")

if __name__ == "__main__":
    test_ocr()