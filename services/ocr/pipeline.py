"""
pipeline.py
-----------

Complete OCR pipeline.
"""

from services.ocr.image_preprocessing import ImagePreprocessor
from services.ocr.ocr_engine import OCREngine

from services.nlp.text_cleaner import TextCleaner
from services.nlp.entity_extraction import EntityExtractor

from services.ocr.validator import OCRValidator

class OCRPipeline:

    def __init__(self):

        self.preprocessor = ImagePreprocessor()

        self.ocr = OCREngine()

        self.cleaner = TextCleaner()

        self.extractor = EntityExtractor()

        self.validator = OCRValidator()

    def process(self, filepath):

        # -----------------------------
        # Image Preprocessing
        # -----------------------------
        pages = self.preprocessor.preprocess_document(filepath)

        # -----------------------------
        # OCR
        # -----------------------------
        ocr_result = self.ocr.extract_document(pages)

        raw_text = ocr_result["text"]
        confidence = ocr_result["confidence"]

        # -----------------------------
        # Text Cleaning
        # -----------------------------
        clean_text = self.cleaner.clean(raw_text)

        # -----------------------------
        # Entity Extraction
        # -----------------------------
        entities = self.extractor.extract(clean_text)

        # -----------------------------
        # Validation
        # -----------------------------
        validation = self.validator.validate(entities)

        # -----------------------------
        # Return
        # -----------------------------
        return {

            "raw_text": raw_text,

            "clean_text": clean_text,

            "entities": entities,

            "confidence": confidence,

            "valid": validation["valid"],

            "missing": validation["missing"],

            "errors": validation["errors"]

        }