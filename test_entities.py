
from services.ocr.image_preprocessing import ImagePreprocessor
from services.ocr.ocr_engine import OCREngine
from services.nlp.text_cleaner import TextCleaner
from services.nlp.entity_extraction import EntityExtractor

# Step 1
processor = ImagePreprocessor()

pages = processor.preprocess_document(
    "testing/sample_documents/form16.pdf"
)

# Step 2
ocr = OCREngine()

ocr_result = ocr.extract_document(pages)

# Step 3
cleaner = TextCleaner()

clean_text = cleaner.clean(ocr_result["text"])

# Step 4
extractor = EntityExtractor()

entities = extractor.extract(clean_text)

print("\n===== ENTITIES =====\n")

for key, value in entities.items():
    print(f"{key:25} : {value}")