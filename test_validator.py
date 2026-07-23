from services.ocr.pipeline import OCRPipeline
from services.ocr.validator import OCRValidator

pipeline = OCRPipeline()

result = pipeline.process("testing/sample_documents/form16.pdf")

validator = OCRValidator()

validation = validator.validate(result["entities"])

print("\n===== VALIDATION RESULT =====\n")

print("Valid :", validation["valid"])

print("\nMissing Fields:")

for field in validation["missing"]:
    print("-", field)

print("\nErrors:")

for err in validation["errors"]:
    print("-", err)