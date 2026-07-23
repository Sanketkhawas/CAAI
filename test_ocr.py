from services.ocr.image_preprocessing import ImagePreprocessor
import cv2

processor = ImagePreprocessor()

pages = processor.pdf_to_images("testing/sample_documents/form16.pdf")

image = processor.pil_to_cv(pages[0])

processed = processor.preprocess(image)

cv2.imwrite("testing/output/page1.jpg", processed)

print("PDF preprocessing successful!")