"""
OCR Configuration
"""

import os

# PDF Conversion
OCR_DPI = 300

# Image preprocessing
RESIZE_SCALE = 1.5

# Allowed file types
ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg"
}

# Poppler path (Windows)
POPPLER_PATH = r"poppler-26.02.0\Library\bin"

# Temporary folder
TEMP_FOLDER = "uploads/temp"

# Logging
LOG_FILE = "logs/ocr.log"