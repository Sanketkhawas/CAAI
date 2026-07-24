
"""
ocr_engine.py
-------------

Performs OCR using EasyOCR.
"""

import easyocr
from services.ocr.logger import logger
from services.ocr.exceptions import OCRException

class OCREngine:

    def __init__(self, languages=["en"]):
        logger.info("Loading EasyOCR Reader...")

        self.reader = easyocr.Reader(
            languages,
            gpu=False
        )

        logger.info("EasyOCR Loaded Successfully.")

    def extract_text(self, image):

        try:

            results = self.reader.readtext(image)

            text = []
            confidence = []

            for (_, detected_text, conf) in results:
                text.append(detected_text)
                confidence.append(conf)

            final_text = "\n".join(text)

            avg_conf = (
                sum(confidence) / len(confidence)
                if confidence else 0
            )

            logger.info("OCR extraction completed.")

            return {
                "text": final_text,
                "confidence": round(avg_conf, 3)
            }

        except Exception as e:

            logger.error(str(e))

            raise OCRException(str(e))

    def extract_document(self, pages):

        full_text = []

        confidences = []

        for page in pages:

            result = self.extract_text(page)

            full_text.append(result["text"])

            confidences.append(result["confidence"])

        avg = (
            sum(confidences) / len(confidences)
            if confidences else 0
        )

        return {
            "text": "\n\n".join(full_text),
            "confidence": round(avg, 3)
        }