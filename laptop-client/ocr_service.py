"""
OCR Service for Debug Duck
Captures screenshots and extracts text using mss and pytesseract
"""

import mss
import pytesseract
from PIL import Image
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure pytesseract path for Windows
# Update this path if Tesseract is installed elsewhere
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Verify Tesseract is available
def verify_tesseract():
    """Check if Tesseract is properly installed and accessible"""
    tesseract_path = pytesseract.pytesseract.tesseract_cmd
    if not os.path.exists(tesseract_path):
        logger.error(f"Tesseract not found at: {tesseract_path}")
        return False
    logger.info(f"Tesseract found at: {tesseract_path}")
    return True


def capture_and_ocr():
    """
    Captures a screenshot of the primary monitor and runs OCR to extract text.

    Returns:
        str: The extracted text from the screenshot, or an error message if OCR fails
    """
    logger.info("Starting screenshot capture and OCR process")

    # First verify Tesseract is available
    if not verify_tesseract():
        error_msg = "Could not capture screen - Tesseract OCR not found"
        logger.error(error_msg)
        return error_msg

    try:
        logger.debug("Initializing mss for screenshot capture")
        with mss.mss() as sct:
            # Get the first monitor (primary display)
            try:
                monitor = sct.monitors[1]
                logger.debug(f"Monitor info: {monitor}")
            except IndexError:
                error_msg = "Could not capture screen - No monitor detected"
                logger.error(error_msg)
                return error_msg

            # Capture the screen
            try:
                logger.info("Capturing screenshot...")
                sct_img = sct.grab(monitor)
                logger.debug(f"Screenshot captured: size={sct_img.size}")
            except Exception as e:
                error_msg = "Could not capture screen"
                logger.error(f"{error_msg}: {str(e)}")
                return error_msg

            # Convert to a PIL Image for pytesseract
            try:
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                logger.debug("Screenshot converted to PIL Image")
            except Exception as e:
                error_msg = "Could not capture screen - Image conversion failed"
                logger.error(f"{error_msg}: {str(e)}")
                return error_msg

            # Run OCR
            try:
                logger.info("Running OCR on screenshot...")
                text = pytesseract.image_to_string(img)
                logger.debug(f"OCR completed, extracted {len(text)} characters")
            except pytesseract.TesseractNotFoundError:
                error_msg = "Could not capture screen - Tesseract executable not found"
                logger.error(error_msg)
                return error_msg
            except Exception as e:
                error_msg = "Could not capture screen - OCR processing failed"
                logger.error(f"{error_msg}: {str(e)}")
                return error_msg

            # Check if any text was found
            if text.strip():
                logger.info(f"OCR SUCCESS: Extracted {len(text)} characters")
                return text
            else:
                error_msg = "No code detected"
                logger.warning(error_msg + " - Screen may be blank or contain only images")
                return error_msg

    except Exception as e:
        error_msg = "Could not capture screen"
        logger.error(f"{error_msg}: Unexpected error - {str(e)}")
        return error_msg


def capture_region_and_ocr(x, y, width, height):
    """
    Captures a specific region of the screen and runs OCR.

    Args:
        x (int): Left coordinate
        y (int): Top coordinate
        width (int): Width of region
        height (int): Height of region

    Returns:
        str: The extracted text from the screenshot region
    """
    logger.info(f"Starting region screenshot capture: ({x}, {y}, {width}, {height})")

    # First verify Tesseract is available
    if not verify_tesseract():
        error_msg = "Could not capture screen - Tesseract OCR not found"
        logger.error(error_msg)
        return error_msg

    try:
        # Validate region parameters
        if width <= 0 or height <= 0:
            error_msg = "Could not capture screen - Invalid region dimensions"
            logger.error(f"{error_msg}: width={width}, height={height}")
            return error_msg

        logger.debug("Initializing mss for region capture")
        with mss.mss() as sct:
            # Define the region to capture
            monitor = {
                "top": y,
                "left": x,
                "width": width,
                "height": height
            }

            # Capture the region
            try:
                logger.info(f"Capturing region...")
                sct_img = sct.grab(monitor)
                logger.debug(f"Region captured: size={sct_img.size}")
            except Exception as e:
                error_msg = "Could not capture screen"
                logger.error(f"{error_msg}: Region capture failed - {str(e)}")
                return error_msg

            # Convert to PIL Image
            try:
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                logger.debug("Region screenshot converted to PIL Image")
            except Exception as e:
                error_msg = "Could not capture screen - Image conversion failed"
                logger.error(f"{error_msg}: {str(e)}")
                return error_msg

            # Run OCR
            try:
                logger.info("Running OCR on region...")
                text = pytesseract.image_to_string(img)
                logger.debug(f"Region OCR completed, extracted {len(text)} characters")
            except pytesseract.TesseractNotFoundError:
                error_msg = "Could not capture screen - Tesseract executable not found"
                logger.error(error_msg)
                return error_msg
            except Exception as e:
                error_msg = "Could not capture screen - OCR processing failed"
                logger.error(f"{error_msg}: {str(e)}")
                return error_msg

            # Check if any text was found
            if text.strip():
                logger.info(f"Region OCR SUCCESS: Extracted {len(text)} characters")
                return text
            else:
                error_msg = "No code detected"
                logger.warning(error_msg + " - Region may be blank or contain only images")
                return error_msg

    except Exception as e:
        error_msg = "Could not capture screen"
        logger.error(f"{error_msg}: Unexpected error in region capture - {str(e)}")
        return error_msg


# Test the OCR service
if __name__ == "__main__":
    # Set logging to DEBUG for testing
    logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("TESTING OCR SERVICE")
    logger.info("=" * 60)

    # Test full screen capture
    logger.info("\nTest 1: Full screen OCR")
    result = capture_and_ocr()

    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    if result.startswith("Could not capture screen") or result == "No code detected":
        print(f"ERROR: {result}")
    else:
        print(f"SUCCESS: Extracted {len(result)} characters")
        print(f"\nFirst 300 chars:\n{result[:300]}")
    print("=" * 60)
