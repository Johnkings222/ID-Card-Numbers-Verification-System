# Quick Start Guide

## Installation

1. **Install system dependencies (Tesseract OCR)**:

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
   ```

   **macOS:**
   ```bash
   brew install tesseract tesseract-lang
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python id_card_verifier.py
   ```

## Testing the Verification Logic

Run the test script to verify everything works:

```bash
python test_verifier.py
```

Expected output: ✅ All tests passed!

## Using the Application

### Step 1: Upload Image
- Click "📁 Upload ID Card Image"
- Select a Chinese ID card image (PNG, JPG, etc.)
- Image will display on the left side

### Step 2: Extract & Verify
- Click "🔍 Extract & Verify"
- Watch the status bar for progress:
  - "Processing... ⏳"
  - "Preprocessing image..."
  - "Extracting text..."
  - "Verifying ID number..."
- Results appear on the right side

### Step 3: Review Results
The system displays:
- **Extracted ID Number**: The 18-digit ID found in the image
- **Verification Result**:
  - ✅ VALID ID CARD (if all checks pass)
  - ❌ INVALID ID CARD (with specific reason)
- **Status Bar**: Shows current status

### Step 4: Save Results (Optional)
- Click "💾 Save Result"
- Data is appended to `results.csv`
- Includes: filename, ID number, status, timestamp

### Step 5: Clear (Start Over)
- Click "🗑️ Clear"
- Resets the entire interface
- Ready for next ID card

## Test ID Numbers

Use these for testing without an actual ID card image:

**Valid IDs:**
- `11010519491231002X` (Beijing, 1949)
- `440524198001010013` (Guangdong, 1980)
- `510102198901010017` (Sichuan, 1989)

**Invalid IDs (for testing error handling):**
- `11010519491231002Y` (wrong checksum)
- `110105194913310020` (invalid month: 13)
- `11010519491232002X` (invalid day: 32)

## Creating Test Images

To create test images for OCR:

1. Create a simple image with ID number text
2. Use a clear, readable font (e.g., Arial, 20-24pt)
3. White background, black text works best
4. Include just the 18-digit number

Example using ImageMagick:
```bash
convert -size 600x100 xc:white -font Arial -pointsize 32 \
  -fill black -gravity center -annotate +0+0 "11010519491231002X" \
  test_id.png
```

Or using Python PIL:
```python
from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (600, 100), color='white')
draw = ImageDraw.ImageDraw(img)
draw.text((50, 30), "11010519491231002X", fill='black')
img.save('test_id.png')
```

## Troubleshooting

### No OCR library available
```bash
pip install pytesseract easyocr
```

### Tesseract not found
```bash
# Check if installed
tesseract --version

# If not found, install it (Ubuntu)
sudo apt-get install tesseract-ocr
```

### Poor OCR accuracy
- Ensure image is clear and high resolution
- ID number should be clearly visible
- Good lighting, no glare
- Straight-on photo (not angled)

### GUI not appearing
- Make sure tkinter is installed (usually comes with Python)
- On Linux, you may need: `sudo apt-get install python3-tk`

## What Gets Verified?

The system checks:

1. **Length**: Must be exactly 18 characters
2. **Address Code**: First 6 digits (must be numeric)
3. **Birth Date**: Characters 7-14 (valid YYYYMMDD format)
4. **Sequence Code**: Characters 15-17 (must be numeric)
5. **Checksum**: Character 18 (calculated using weighted algorithm)

All checks must pass for a ✅ VALID result.

## Output Files

- `results.csv` - Created when you save results
- Contains: filename, extracted_id, verification_status, timestamp

## Need Help?

See the full [README.md](README.md) for detailed documentation.
