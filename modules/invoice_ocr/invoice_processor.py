"""
Invoice Photo Processor
Handles image preprocessing and OCR text extraction from invoice photos
"""

import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json


class InvoiceProcessor:
    """Process invoice photos and extract text using OCR"""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize the invoice processor

        Args:
            tesseract_cmd: Optional path to tesseract executable
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess invoice image for better OCR results

        Args:
            image_path: Path to the invoice image

        Returns:
            Preprocessed image as numpy array
        """
        # Read image
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # Apply adaptive thresholding for better text extraction
        # This works well for invoices with varying lighting
        thresh = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        # Deskew image if needed
        thresh = self._deskew_image(thresh)

        # Optional: Apply morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        return cleaned

    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Detect and correct skew in the image

        Args:
            image: Input image

        Returns:
            Deskewed image
        """
        # Detect edges
        edges = cv2.Canny(image, 50, 150, apertureSize=3)

        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

        if lines is None:
            return image

        # Calculate average angle
        angles = []
        for rho, theta in lines[:, 0]:
            angle = theta * 180 / np.pi
            # Filter for nearly horizontal lines
            if 85 < angle < 95 or -5 < angle < 5:
                angles.append(angle)

        if not angles:
            return image

        # Calculate median angle
        median_angle = np.median(angles)

        # Adjust angle to be relative to horizontal
        if median_angle > 45:
            angle_to_rotate = median_angle - 90
        else:
            angle_to_rotate = median_angle

        # Only rotate if skew is significant (> 0.5 degrees)
        if abs(angle_to_rotate) > 0.5:
            # Get image center
            height, width = image.shape[:2]
            center = (width // 2, height // 2)

            # Rotate image
            rotation_matrix = cv2.getRotationMatrix2D(center, angle_to_rotate, 1.0)
            rotated = cv2.warpAffine(
                image, rotation_matrix, (width, height),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated

        return image

    def extract_text(self, image_path: str, preprocess: bool = True) -> str:
        """
        Extract text from invoice image using OCR

        Args:
            image_path: Path to the invoice image
            preprocess: Whether to preprocess the image

        Returns:
            Extracted text as string
        """
        if preprocess:
            # Preprocess and use the numpy array
            processed_img = self.preprocess_image(image_path)

            # Convert to PIL Image for pytesseract
            pil_img = Image.fromarray(processed_img)
        else:
            # Use original image
            pil_img = Image.open(image_path)

        # Extract text with pytesseract
        # Use custom config for better results
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(pil_img, config=custom_config)

        return text

    def extract_text_with_boxes(self, image_path: str, preprocess: bool = True) -> List[Dict]:
        """
        Extract text with bounding box information

        Args:
            image_path: Path to the invoice image
            preprocess: Whether to preprocess the image

        Returns:
            List of dictionaries containing text and position data
        """
        if preprocess:
            processed_img = self.preprocess_image(image_path)
            pil_img = Image.fromarray(processed_img)
        else:
            pil_img = Image.open(image_path)

        # Get detailed OCR data
        data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)

        # Parse the data
        text_boxes = []
        n_boxes = len(data['text'])

        for i in range(n_boxes):
            # Filter out empty text
            if int(data['conf'][i]) > 0:  # Only include confident detections
                text_boxes.append({
                    'text': data['text'][i],
                    'confidence': int(data['conf'][i]),
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'line_num': data['line_num'][i],
                    'block_num': data['block_num'][i]
                })

        return text_boxes

    def save_preprocessed_image(self, image_path: str, output_path: str) -> None:
        """
        Save preprocessed version of image for debugging

        Args:
            image_path: Path to the invoice image
            output_path: Path to save preprocessed image
        """
        processed_img = self.preprocess_image(image_path)
        cv2.imwrite(output_path, processed_img)

    def process_invoice(self, image_path: str) -> Dict:
        """
        Full pipeline: preprocess and extract text from invoice

        Args:
            image_path: Path to the invoice image

        Returns:
            Dictionary with raw text and metadata
        """
        # Extract text
        text = self.extract_text(image_path, preprocess=True)

        # Get text with boxes for more detailed analysis
        text_boxes = self.extract_text_with_boxes(image_path, preprocess=True)

        return {
            'image_path': image_path,
            'raw_text': text,
            'text_boxes': text_boxes,
            'total_lines': len(set(box['line_num'] for box in text_boxes)),
            'average_confidence': np.mean([box['confidence'] for box in text_boxes]) if text_boxes else 0
        }

    def batch_process(self, image_paths: List[str]) -> List[Dict]:
        """
        Process multiple invoice images

        Args:
            image_paths: List of paths to invoice images

        Returns:
            List of processing results
        """
        results = []

        for image_path in image_paths:
            try:
                result = self.process_invoice(image_path)
                results.append(result)
            except Exception as e:
                results.append({
                    'image_path': image_path,
                    'error': str(e),
                    'raw_text': '',
                    'text_boxes': []
                })

        return results
