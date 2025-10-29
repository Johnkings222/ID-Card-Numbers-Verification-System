# Chinese ID Card Verification System

Automatic Identification and Verification System for Chinese ID Card Numbers Based on Image Processing.

## Features

- **Image Upload**: Support for multiple image formats (PNG, JPG, JPEG, BMP, TIFF)
- **OCR Processing**: Dual OCR support (Pytesseract + EasyOCR fallback)
- **Image Preprocessing**: Advanced OpenCV preprocessing (grayscale, denoising, thresholding)
- **ID Extraction**: Automatic extraction of 18-digit Chinese ID numbers
- **Verification**: Complete validation including:
  - Length check (18 characters)
  - Address code validation (first 6 digits)
  - Birth date validation (YYYYMMDD format)
  - Sequence code validation (3 digits)
  - Checksum verification (Chinese ID algorithm)
- **Result Export**: Save results to CSV file with timestamp
- **User-Friendly GUI**: Clean Tkinter interface with visual feedback

## Requirements

### System Requirements

- Python 3.7+
- Tesseract OCR (for pytesseract)

### Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- opencv-python
- pytesseract
- Pillow
- easyocr (optional, used as fallback)

### Installing Tesseract OCR

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # Chinese simplified
```

#### macOS:
```bash
brew install tesseract
brew install tesseract-lang  # For Chinese support
```

#### Windows:
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH
3. Set tesseract path in code if needed:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

## Installation

1. Clone or download this repository

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Tesseract OCR (see above)

4. Run the application:
   ```bash
   python id_card_verifier.py
   ```

## Usage

1. **Upload Image**: Click "Upload ID Card Image" to select an ID card image

2. **Extract & Verify**: Click "Extract & Verify" to process the image:
   - Image is preprocessed using OpenCV
   - OCR extracts text from the image
   - 18-digit ID number is extracted using regex
   - Number is validated using Chinese ID verification algorithm

3. **View Results**:
   - Extracted ID number appears in the top text box
   - Verification result shows validation status
   - Status bar shows current operation status

4. **Save Results**: Click "Save Result" to export to `results.csv`

5. **Clear**: Click "Clear" to reset the interface

## Chinese ID Card Format

Chinese ID numbers are 18 characters:
- **Positions 1-6**: Address code (administrative division)
- **Positions 7-14**: Birth date (YYYYMMDD)
- **Positions 15-17**: Sequence code (odd=male, even=female)
- **Position 18**: Checksum digit (calculated using weighted algorithm)

### Checksum Algorithm

The last digit is calculated as follows:

1. Multiply each of the first 17 digits by weights:
   ```
   [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
   ```

2. Sum all products

3. Take modulo 11

4. Map result to checksum:
   ```
   ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
   ```

## Example ID Numbers

For testing purposes (these are valid test IDs with correct checksums):

**Valid Format:**
- 11010519491231002X (Beijing, 1949)
- 440524198001010013 (Guangdong, 1980)
- 510102198901010017 (Sichuan, 1989)

## File Structure

```
ID Card Numbers Verification System/
│
├── id_card_verifier.py      # Main application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── results.csv              # Generated after saving results
```

## Troubleshooting

### OCR Not Working

**Issue**: "No OCR library available"
- **Solution**: Install pytesseract or easyocr
  ```bash
  pip install pytesseract easyocr
  ```

**Issue**: Tesseract not found
- **Solution**: Install Tesseract OCR and ensure it's in PATH

### Poor OCR Accuracy

**Issue**: ID number not extracted correctly
- **Solution**:
  - Ensure image is clear and well-lit
  - ID number should be clearly visible
  - Try different image formats
  - Adjust preprocessing parameters in code

### Image Not Displaying

**Issue**: Image upload successful but not showing
- **Solution**: Check image format is supported
- Ensure Pillow is installed: `pip install Pillow`

## Technical Details

### Image Preprocessing Pipeline

1. **Grayscale Conversion**: Simplify to single channel
2. **Denoising**: Remove noise using fastNlMeansDenoising
3. **Adaptive Thresholding**: Binary conversion for better OCR

### OCR Strategy

- **Primary**: Pytesseract (faster, good for clear images)
- **Fallback**: EasyOCR (more accurate, slower)
- Configuration optimized for digits and 'X' character

### Verification Logic

The application performs comprehensive validation:
1. Format check (18 characters)
2. Address code validation (numeric, 6 digits)
3. Date validation (valid YYYYMMDD)
4. Sequence code check (numeric, 3 digits)
5. Checksum verification (weighted algorithm)

## CSV Output Format

The `results.csv` file contains:
- `filename`: Name of the uploaded image
- `extracted_id`: Extracted ID number
- `verification_status`: Valid/Invalid
- `timestamp`: When the verification was performed

## License

This project is for educational purposes.

## Contributing

Feel free to submit issues or pull requests for improvements.
