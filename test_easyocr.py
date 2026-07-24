from services.ocr.image_preprocessing import ImagePreprocessor
from services.ocr.ocr_engine import OCREngine

processor = ImagePreprocessor()
ocr = OCREngine()

pages = processor.preprocess_document(
    "testing/sample_documents/form16.pdf"
)

result = ocr.extract_document(pages)

print("\n===== OCR RESULT =====\n")
print(result["text"])

print("\nConfidence:", result["confidence"])