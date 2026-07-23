"""
image_preprocessing.py
----------------------

Preprocesses uploaded documents before OCR.

Features:
- PDF to Images
- Image Loading
- Resize
- Grayscale
- Noise Removal
- Thresholding
- Deskew
- Logging
- Exception Handling

"""

import cv2
import numpy as np
from pdf2image import convert_from_path

from services.ocr.logger import logger

from services.ocr.config import (
    OCR_DPI,
    RESIZE_SCALE,
    POPPLER_PATH,
    ALLOWED_EXTENSIONS
)

from services.ocr.exceptions import (
    InvalidFileException,
    PDFConversionException,
    ImageReadException
)


class ImagePreprocessor:
    """
    Handles all preprocessing operations before OCR.

    """

    def __init__(self):
        logger.info("ImagePreprocessor initialized")

    # ---------------------------------------------------------
    # PDF → Images
    # ---------------------------------------------------------
    def pdf_to_images(self, pdf_path):
        """
        Converts every page of a PDF into PIL Images.
        
        """
        print("Poppler:", POPPLER_PATH)
        try:
            logger.info(f"Converting PDF: {pdf_path}")

            pages = convert_from_path(
                pdf_path,
                dpi=OCR_DPI,
                poppler_path=POPPLER_PATH
            )

            logger.info(f"{len(pages)} page(s) converted successfully")

            return pages

        except Exception as e:
            logger.error(f"PDF Conversion Failed: {e}")
            raise PDFConversionException(str(e))

    # ---------------------------------------------------------
    # PIL → OpenCV
    # ---------------------------------------------------------
    def pil_to_cv(self, image):
        """
        Converts PIL image into OpenCV format.
        """

        return cv2.cvtColor(
            np.array(image),
            cv2.COLOR_RGB2BGR
        )

    # ---------------------------------------------------------
    # Read Image
    # ---------------------------------------------------------
    def read_image(self, image_path):
        """
        Reads an image using OpenCV.
        """

        image = cv2.imread(image_path)

        if image is None:
            logger.error(f"Unable to read image: {image_path}")
            raise ImageReadException(image_path)

        logger.info(f"Image Loaded: {image_path}")

        return image

    # ---------------------------------------------------------
    # Resize
    # ---------------------------------------------------------
    def resize_image(self, image, scale=RESIZE_SCALE):
        """
        Enlarges image for better OCR.
        """

        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)

        resized = cv2.resize(
            image,
            (width, height),
            interpolation=cv2.INTER_CUBIC
        )

        logger.info("Image resized")

        return resized

    # ---------------------------------------------------------
    # Grayscale
    # ---------------------------------------------------------
    def grayscale(self, image):
        """
        Converts image to grayscale.
        """

        logger.info("Converted to grayscale")

        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

    # ---------------------------------------------------------
    # Noise Removal
    # ---------------------------------------------------------
    def remove_noise(self, image):
        """
        Removes image noise.
        """

        logger.info("Noise removed")

        return cv2.fastNlMeansDenoising(image)

    # ---------------------------------------------------------
    # Threshold
    # ---------------------------------------------------------
    def threshold(self, image):
        """
        Converts image to black & white.
        """

        _, thresh = cv2.threshold(
            image,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        logger.info("Threshold applied")

        return thresh

    # ---------------------------------------------------------
    # Deskew
    # ---------------------------------------------------------
    def deskew(self, image):
        """
        Straightens tilted documents.
        """

        coords = np.column_stack(np.where(image > 0))

        if len(coords) == 0:
            logger.warning("Deskew skipped (no text detected)")
            return image

        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = 90 + angle

        (h, w) = image.shape[:2]

        center = (w // 2, h // 2)

        matrix = cv2.getRotationMatrix2D(
            center,
            angle,
            1.0
        )

        rotated = cv2.warpAffine(
            image,
            matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        logger.info(f"Deskew completed (angle={angle:.2f})")

        return rotated

    # ---------------------------------------------------------
    # Complete Pipeline
    # ---------------------------------------------------------
    def preprocess(self, image):
        """
        Complete preprocessing pipeline.
        """

        logger.info("Starting preprocessing pipeline")

        image = self.resize_image(image)

        image = self.grayscale(image)

        image = self.remove_noise(image)

        image = self.threshold(image)

        image = self.deskew(image)

        logger.info("Preprocessing completed")

        return image

    # ---------------------------------------------------------
    # Preprocess Document
    # ---------------------------------------------------------
    def preprocess_document(self, file_path):
        """
        Processes any supported document and returns
        OCR-ready image(s).
        """

        extension = file_path.split(".")[-1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            logger.error(f"Unsupported file type: {extension}")
            raise InvalidFileException(extension)

        logger.info(f"Processing document: {file_path}")

        # ---------------- PDF ----------------
        if extension == "pdf":

            pages = self.pdf_to_images(file_path)

            processed_pages = []

            for page in pages:

                image = self.pil_to_cv(page)

                processed_pages.append(
                    self.preprocess(image)
                )

            logger.info(
                f"Successfully processed {len(processed_pages)} page(s)"
            )

            return processed_pages

        # ---------------- IMAGE ----------------
        image = self.read_image(file_path)

        processed_image = self.preprocess(image)

        logger.info("Image preprocessing completed")

        return [processed_image]