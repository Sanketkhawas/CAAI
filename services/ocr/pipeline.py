
"""
pipeline.py
-----------
OCR, cleaning, entity extraction and validation pipeline.
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

    def process(self, filepath, document_type="form16"):

        # 1. Preprocess PDF or image
        pages = self.preprocessor.preprocess_document(filepath)

        # 2. Extract OCR text
        ocr_result = self.ocr.extract_document(pages)

        raw_text = ocr_result.get("text", "") or ""
        confidence = ocr_result.get("confidence", 0)

        if not raw_text.strip():
            raise ValueError(
                f"OCR returned empty text for {filepath}"
            )

        # 3. Clean OCR text
        clean_text = self.cleaner.clean(raw_text)

        if not clean_text or not clean_text.strip():
            raise ValueError(
                f"Text cleaning returned empty text for {filepath}"
            )

        # 4. Extract fields for the correct document type
        entities = self.extractor.extract(
            clean_text,
            document_type=document_type
        )

        # 5. Validate extracted fields
        validation = self.validator.validate(
            entities,
            document_type=document_type
        )

        # 6. Return the pipeline result
        return {
            "raw_text": raw_text,
            "clean_text": clean_text,
            "entities": entities,
            "confidence": confidence,
            "valid": validation.get("valid", False),
            "missing": validation.get("missing", []),
            "errors": validation.get("errors", []),
        }
