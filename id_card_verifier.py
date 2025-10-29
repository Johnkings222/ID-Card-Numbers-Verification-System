#!/usr/bin/env python3
"""
Automatic Identification and Verification System for Chinese ID Card Numbers
Based on Image Processing
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import re
import csv
from datetime import datetime
import os
import platform
import sys

# OCR imports
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True

    # Windows-specific Tesseract path configuration
    if platform.system() == 'Windows':
        # Common installation paths on Windows
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
        ]

        # Try to find Tesseract in common locations
        tesseract_found = False
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                tesseract_found = True
                print(f"Tesseract found at: {path}")
                break

        if not tesseract_found:
            print("警告：未找到 Tesseract OCR。请确保已安装并配置正确的路径。")
            print("下载地址：https://github.com/UB-Mannheim/tesseract/wiki")

except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("pytesseract not available")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("easyocr not available")


class ChineseIDVerifier:
    """Chinese ID Card Number Verification Logic"""

    # Weighted factors for first 17 digits
    WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]

    # Checksum mapping
    CHECKSUM_MAP = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    @staticmethod
    def extract_id_number(text):
        """Extract 18-digit Chinese ID number from text using regex"""
        # Pattern for 18-digit ID: 17 digits + (digit or X)
        pattern = r'\b\d{17}[\dXx]\b'
        matches = re.findall(pattern, text)

        if matches:
            # Return first match, convert x to X
            return matches[0].upper()
        return None

    @staticmethod
    def validate_address_code(id_number):
        """Validate first 6 digits (address code)"""
        address_code = id_number[:6]
        return address_code.isdigit()

    @staticmethod
    def validate_birth_date(id_number):
        """Validate birth date (positions 7-14, YYYYMMDD)"""
        birth_date_str = id_number[6:14]

        if not birth_date_str.isdigit():
            return False

        try:
            year = int(birth_date_str[:4])
            month = int(birth_date_str[4:6])
            day = int(birth_date_str[6:8])

            # Basic validation
            if year < 1900 or year > datetime.now().year:
                return False
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False

            # Try to create a date object to verify validity
            datetime(year, month, day)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_sequence_code(id_number):
        """Validate sequence code (positions 15-17)"""
        sequence_code = id_number[14:17]
        return sequence_code.isdigit()

    @staticmethod
    def validate_checksum(id_number):
        """Validate checksum digit using Chinese ID algorithm"""
        if len(id_number) != 18:
            return False

        # Calculate weighted sum of first 17 digits
        weighted_sum = 0
        for i in range(17):
            digit = int(id_number[i])
            weighted_sum += digit * ChineseIDVerifier.WEIGHTS[i]

        # Get checksum index
        checksum_index = weighted_sum % 11
        expected_checksum = ChineseIDVerifier.CHECKSUM_MAP[checksum_index]

        # Compare with actual last digit
        actual_checksum = id_number[17].upper()
        return actual_checksum == expected_checksum

    @classmethod
    def verify_id(cls, id_number):
        """
        Complete verification of Chinese ID number
        Returns: (is_valid, error_message)
        """
        if not id_number:
            return False, "未找到身份证号码"

        # Check length
        if len(id_number) != 18:
            return False, f"长度无效：{len(id_number)}位（应为18位）"

        # Validate address code
        if not cls.validate_address_code(id_number):
            return False, "地址码无效（前6位）"

        # Validate birth date
        if not cls.validate_birth_date(id_number):
            return False, "出生日期无效"

        # Validate sequence code
        if not cls.validate_sequence_code(id_number):
            return False, "顺序码无效"

        # Validate checksum
        if not cls.validate_checksum(id_number):
            return False, "校验码无效"

        return True, "身份证号码格式有效"


class ImageProcessor:
    """Image preprocessing for OCR"""

    @staticmethod
    def preprocess_image(image_path):
        """
        Preprocess image for better OCR results
        Returns: list of preprocessed images to try
        """
        # Read image
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError("Unable to read image")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # Create multiple preprocessed versions
        processed_images = []

        # 1. Adaptive thresholding
        adaptive = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        processed_images.append(adaptive)

        # 2. Otsu's thresholding
        _, otsu = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(otsu)

        # 3. Simple denoised grayscale (no thresholding)
        processed_images.append(denoised)

        # 4. Enhanced contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        processed_images.append(enhanced)

        return processed_images

    @staticmethod
    def extract_text_pytesseract(image):
        """Extract text using pytesseract"""
        if not PYTESSERACT_AVAILABLE:
            return None

        try:
            # Try multiple configurations to maximize extraction success
            configs = [
                '--oem 3 --psm 6',  # Default: assume uniform block of text
                '--oem 3 --psm 11',  # Sparse text
                '--oem 3 --psm 12',  # Sparse text with OSD
                '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789X',  # Numbers only
            ]

            all_text = []
            for config in configs:
                try:
                    text = pytesseract.image_to_string(image, lang='chi_sim+eng', config=config)
                    if text:
                        all_text.append(text)
                except:
                    continue

            # Combine all results
            return '\n'.join(all_text)
        except Exception as e:
            print(f"Pytesseract error: {e}")
            return None

    @staticmethod
    def extract_text_easyocr(image_path):
        """Extract text using EasyOCR"""
        if not EASYOCR_AVAILABLE:
            return None

        try:
            reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            results = reader.readtext(image_path)

            # Combine all detected text
            text = ' '.join([result[1] for result in results])
            return text
        except Exception as e:
            print(f"EasyOCR error: {e}")
            return None


class IDCardVerifierGUI:
    """Main GUI Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("中国身份证号码验证系统")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # Variables
        self.image_path = None
        self.extracted_id = None
        self.verification_status = None
        self.original_image = None

        # Initialize OCR reader for EasyOCR (if available)
        self.easyocr_reader = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""

        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="中国身份证号码验证系统",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)

        # Main content area
        content_frame = tk.Frame(self.root, bg="#ecf0f1")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left side - Image display
        left_frame = tk.LabelFrame(
            content_frame,
            text="已上传的身份证图片",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1"
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.image_canvas = tk.Canvas(left_frame, bg="white", width=400, height=300)
        self.image_canvas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Right side - Results display
        right_frame = tk.LabelFrame(
            content_frame,
            text="识别与验证结果",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1"
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Extracted ID display
        tk.Label(
            right_frame,
            text="提取的身份证号码：",
            font=("Arial", 10, "bold"),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))

        self.id_text = tk.Text(
            right_frame,
            height=2,
            font=("Courier", 14, "bold"),
            bg="white",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.id_text.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.id_text.config(state=tk.DISABLED)

        # Verification result display
        tk.Label(
            right_frame,
            text="验证结果：",
            font=("Arial", 10, "bold"),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))

        self.result_text = tk.Text(
            right_frame,
            height=8,
            font=("Arial", 11),
            bg="white",
            relief=tk.SUNKEN,
            borderwidth=2,
            wrap=tk.WORD
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.result_text.config(state=tk.DISABLED)

        # Button frame
        button_frame = tk.Frame(self.root, bg="#ecf0f1")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Buttons
        btn_style = {
            "font": ("Arial", 10, "bold"),
            "width": 18,
            "height": 2,
            "relief": tk.RAISED,
            "borderwidth": 2
        }

        self.upload_btn = tk.Button(
            button_frame,
            text="上传身份证图片",
            command=self.upload_image,
            bg="#3498db",
            fg="white",
            **btn_style
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5)

        self.extract_btn = tk.Button(
            button_frame,
            text="识别并验证",
            command=self.extract_and_verify,
            bg="#000080",
            fg="white",
            state=tk.DISABLED,
            **btn_style
        )
        self.extract_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = tk.Button(
            button_frame,
            text="保存结果",
            command=self.save_result,
            bg="#000000",
            fg="white",
            state=tk.DISABLED,
            **btn_style
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(
            button_frame,
            text="清空",
            command=self.clear_all,
            bg="#e74c3c",
            fg="white",
            **btn_style
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_frame = tk.Frame(self.root, bg="#34495e", height=30)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            self.status_frame,
            text="就绪",
            font=("Arial", 9),
            bg="#34495e",
            fg="white",
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def upload_image(self):
        """Handle image upload"""
        file_path = filedialog.askopenfilename(
            title="选择身份证图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            try:
                self.image_path = file_path
                self.display_image(file_path)
                self.extract_btn.config(state=tk.NORMAL)
                self.update_status(f"图片已加载：{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"图片加载失败：\n{str(e)}")
                self.update_status("图片加载出错")

    def display_image(self, image_path):
        """Display image on canvas with auto-resize"""
        # Load image
        image = Image.open(image_path)
        self.original_image = image

        # Get canvas dimensions
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()

        # Use default size if canvas not yet rendered
        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 300

        # Calculate resize ratio
        img_width, img_height = image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)

        new_width = int(img_width * ratio * 0.9)  # 90% of canvas
        new_height = int(img_height * ratio * 0.9)

        # Resize image
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(resized_image)

        # Display on canvas
        self.image_canvas.delete("all")
        self.image_canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=photo, anchor=tk.CENTER
        )
        self.image_canvas.image = photo  # Keep reference

    def extract_and_verify(self):
        """Extract ID number and verify it"""
        if not self.image_path:
            messagebox.showwarning("警告", "请先上传图片！")
            return

        self.update_status("处理中...")
        self.root.update()

        try:
            # Preprocess image - get multiple versions
            self.update_status("预处理图片中...")
            preprocessed_images = ImageProcessor.preprocess_image(self.image_path)

            # Extract text using available OCR - try all preprocessing methods
            all_text = []
            id_number = None

            # Try pytesseract first with all preprocessed versions
            if PYTESSERACT_AVAILABLE:
                self.update_status("使用 Pytesseract 提取文本...")
                for img in preprocessed_images:
                    text = ImageProcessor.extract_text_pytesseract(img)
                    if text:
                        all_text.append(text)
                        # Try to extract ID from this text
                        temp_id = ChineseIDVerifier.extract_id_number(text)
                        if temp_id:
                            id_number = temp_id
                            break  # Found ID, stop trying

            # Fallback to EasyOCR if still no ID found
            if not id_number and EASYOCR_AVAILABLE:
                self.update_status("使用 EasyOCR 提取文本...")
                text = ImageProcessor.extract_text_easyocr(self.image_path)
                if text:
                    all_text.append(text)
                    id_number = ChineseIDVerifier.extract_id_number(text)

            if not all_text:
                raise Exception("没有可用的OCR库或文本提取失败")

            # Extract ID number from all collected text if not already found
            self.update_status("提取身份证号码...")
            if not id_number:
                combined_text = '\n'.join(all_text)
                id_number = ChineseIDVerifier.extract_id_number(combined_text)

            # Verify ID number
            self.update_status("验证身份证号码...")
            is_valid, message = ChineseIDVerifier.verify_id(id_number)

            # Store results
            self.extracted_id = id_number if id_number else "未找到"
            self.verification_status = "有效" if is_valid else "无效"

            # Display results
            self.display_results(id_number, is_valid, message)

            # Enable save button
            self.save_btn.config(state=tk.NORMAL)

            # Update status
            if is_valid:
                self.update_status("验证通过")
            else:
                self.update_status("格式无效")

        except Exception as e:
            messagebox.showerror("错误", f"处理失败：\n{str(e)}")
            self.update_status("处理失败")

    def display_results(self, id_number, is_valid, message):
        """Display extraction and verification results"""
        # Display ID number
        self.id_text.config(state=tk.NORMAL)
        self.id_text.delete(1.0, tk.END)
        if id_number:
            self.id_text.insert(1.0, id_number)
        else:
            self.id_text.insert(1.0, "未找到身份证号码")
        self.id_text.config(state=tk.DISABLED)

        # Display verification result
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        if is_valid:
            result = f"身份证号码有效\n\n"
            result += f"状态：{message}\n\n"
            if id_number and len(id_number) == 18:
                result += f"地址码：{id_number[:6]}\n"
                result += f"出生日期：{id_number[6:14]}\n"
                result += f"顺序码：{id_number[14:17]}\n"
                result += f"校验码：{id_number[17]}"
        else:
            result = f"身份证号码无效\n\n"
            result += f"原因：{message}\n\n"
            if id_number:
                result += f"提取的号码：{id_number}"

        self.result_text.insert(1.0, result)
        self.result_text.config(state=tk.DISABLED)

    def save_result(self):
        """Save result to CSV file"""
        if not self.extracted_id:
            messagebox.showwarning("警告", "没有可保存的结果！")
            return

        try:
            csv_file = "results.csv"
            file_exists = os.path.isfile(csv_file)

            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write header if file doesn't exist
                if not file_exists:
                    writer.writerow([
                        'filename',
                        'extracted_id',
                        'verification_status',
                        'timestamp'
                    ])

                # Write data
                writer.writerow([
                    os.path.basename(self.image_path),
                    self.extracted_id,
                    self.verification_status,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])

            messagebox.showinfo("成功", f"结果已保存到 {csv_file}")
            self.update_status(f"结果已保存到 {csv_file}")

        except Exception as e:
            messagebox.showerror("错误", f"保存结果失败：\n{str(e)}")
            self.update_status("保存结果失败")

    def clear_all(self):
        """Clear all data and reset interface"""
        self.image_path = None
        self.extracted_id = None
        self.verification_status = None
        self.original_image = None

        # Clear canvas
        self.image_canvas.delete("all")

        # Clear text widgets
        self.id_text.config(state=tk.NORMAL)
        self.id_text.delete(1.0, tk.END)
        self.id_text.config(state=tk.DISABLED)

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)

        # Disable buttons
        self.extract_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)

        # Reset status
        self.update_status("就绪")


def main():
    """Main entry point"""
    # Check if at least one OCR library is available
    if not PYTESSERACT_AVAILABLE and not EASYOCR_AVAILABLE:
        print("ERROR: No OCR library available!")
        print("Please install either pytesseract or easyocr:")
        print("  pip install pytesseract")
        print("  pip install easyocr")
        return

    root = tk.Tk()
    app = IDCardVerifierGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
