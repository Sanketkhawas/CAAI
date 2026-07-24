from services.ocr.image_preprocessing import ImagePreprocessor
from services.ocr.ocr_engine import OCREngine
from services.nlp.text_cleaner import TextCleaner

processor = ImagePreprocessor()
ocr = OCREngine()
cleaner = TextCleaner()

# Preprocess
pages = processor.preprocess_document(
    "testing/sample_documents/form16.pdf"
)

# OCR
ocr_result = ocr.extract_document(pages)

# Clean
clean_text = cleaner.clean(ocr_result["text"])

print("\n===== OCR RESULT =====\n")
print(ocr_result["text"])

print("\n===== CLEANED TEXT =====\n")
print(clean_text)