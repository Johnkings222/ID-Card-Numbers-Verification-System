#!/usr/bin/env python3
"""
Debug script to test OCR extraction on ID card images
"""

import cv2
import re
import sys
import os

# Try to import OCR libraries
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("Warning: pytesseract not available")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: easyocr not available")

print("=" * 70)
print("OCR Debug Tool for Chinese ID Cards")
print("=" * 70)
print()

# Check which OCR is available
print("Available OCR Libraries:")
print(f"  - Pytesseract: {'✅ Yes' if PYTESSERACT_AVAILABLE else '❌ No'}")
print(f"  - EasyOCR: {'✅ Yes' if EASYOCR_AVAILABLE else '❌ No'}")
print()

if not PYTESSERACT_AVAILABLE and not EASYOCR_AVAILABLE:
    print("ERROR: No OCR library available!")
    sys.exit(1)


def preprocess_image(image_path, method="adaptive"):
    """Preprocess image with different methods"""
    img = cv2.imread(image_path)

    if img is None:
        print(f"ERROR: Could not read image: {image_path}")
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if method == "adaptive":
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        # Adaptive threshold
        processed = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
    elif method == "otsu":
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        # Otsu's thresholding
        _, processed = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method == "simple":
        # Simple thresholding
        _, processed = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    elif method == "none":
        # No preprocessing
        processed = gray
    else:
        processed = gray

    return processed


def extract_text_pytesseract(image, lang='chi_sim+eng'):
    """Extract text using pytesseract"""
    if not PYTESSERACT_AVAILABLE:
        return None

    try:
        # Try different configurations
        configs = [
            ('Digits+X only', '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789X'),
            ('Default config', '--oem 3 --psm 6'),
            ('Single line', '--oem 3 --psm 7'),
        ]

        results = {}
        for name, config in configs:
            try:
                text = pytesseract.image_to_string(image, lang=lang, config=config)
                results[name] = text.strip()
            except Exception as e:
                results[name] = f"Error: {e}"

        return results
    except Exception as e:
        return {"Error": str(e)}


def extract_text_easyocr(image_path):
    """Extract text using EasyOCR"""
    if not EASYOCR_AVAILABLE:
        return None

    try:
        reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)
        results = reader.readtext(image_path)

        # Combine all detected text
        full_text = ' '.join([result[1] for result in results])

        # Also return detailed results
        detailed = []
        for bbox, text, conf in results:
            detailed.append(f"{text} (confidence: {conf:.2f})")

        return {
            'full_text': full_text,
            'detailed': detailed
        }
    except Exception as e:
        return {"Error": str(e)}


def extract_id_number(text):
    """Extract 18-digit ID number from text"""
    if not text:
        return None

    # Pattern for 18-digit ID
    pattern = r'\b\d{17}[\dXx]\b'
    matches = re.findall(pattern, text)

    if matches:
        return matches[0].upper()

    # Try to find partial matches (for debugging)
    partial_pattern = r'\d{10,}'
    partial_matches = re.findall(partial_pattern, text)

    return None, partial_matches if partial_matches else []


def test_image(image_path):
    """Test OCR on a single image"""
    print("=" * 70)
    print(f"Testing: {os.path.basename(image_path)}")
    print("=" * 70)
    print()

    if not os.path.exists(image_path):
        print(f"ERROR: File not found: {image_path}")
        return

    # Try different preprocessing methods
    methods = ['adaptive', 'otsu', 'simple', 'none']

    for method in methods:
        print(f"--- Preprocessing Method: {method.upper()} ---")

        processed = preprocess_image(image_path, method)
        if processed is None:
            continue

        # Save preprocessed image for inspection
        output_name = f"debug_{os.path.basename(image_path).split('.')[0]}_{method}.png"
        cv2.imwrite(output_name, processed)
        print(f"Saved preprocessed image: {output_name}")

        # Test with Pytesseract
        if PYTESSERACT_AVAILABLE:
            print("\n[Pytesseract Results]")
            results = extract_text_pytesseract(processed)
            if results:
                for config_name, text in results.items():
                    print(f"\n  {config_name}:")
                    print(f"  Extracted text: {repr(text)}")

                    # Try to extract ID
                    result = extract_id_number(text)
                    if isinstance(result, tuple):
                        id_num, partial = result
                        if partial:
                            print(f"  Partial numbers found: {partial}")
                    else:
                        id_num = result

                    if id_num:
                        print(f"  ✅ ID Number found: {id_num}")
                    else:
                        print(f"  ❌ No 18-digit ID found")

        # Test with EasyOCR
        if EASYOCR_AVAILABLE:
            print("\n[EasyOCR Results]")
            results = extract_text_easyocr(image_path)
            if results and 'full_text' in results:
                print(f"  Full text: {repr(results['full_text'])}")
                print(f"  Detailed detections:")
                for detail in results['detailed']:
                    print(f"    - {detail}")

                # Try to extract ID
                result = extract_id_number(results['full_text'])
                if isinstance(result, tuple):
                    id_num, partial = result
                    if partial:
                        print(f"  Partial numbers found: {partial}")
                else:
                    id_num = result

                if id_num:
                    print(f"  ✅ ID Number found: {id_num}")
                else:
                    print(f"  ❌ No 18-digit ID found")

        print()


def main():
    """Main function"""
    # Check for command line arguments
    if len(sys.argv) > 1:
        image_paths = sys.argv[1:]
    else:
        # Look for ID images in current directory
        image_paths = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            import glob
            image_paths.extend(glob.glob(ext))
            image_paths.extend(glob.glob(ext.upper()))

        if not image_paths:
            print("No images found. Usage: python debug_ocr.py <image1> <image2> ...")
            return

    print(f"Found {len(image_paths)} image(s) to test\n")

    for image_path in image_paths:
        test_image(image_path)

    print("=" * 70)
    print("Debug complete! Check the debug_*.png files to see preprocessing results")
    print("=" * 70)


if __name__ == "__main__":
    main()
