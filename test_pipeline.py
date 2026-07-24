from services.ocr.pipeline import OCRPipeline

pipeline = OCRPipeline()

result = pipeline.process(

    "testing/sample_documents/form16.pdf"

)

print(result["entities"])