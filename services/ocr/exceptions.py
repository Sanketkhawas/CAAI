"""
OCR Custom Exceptions
"""


class OCRException(Exception):
    """Base OCR Exception"""
    pass


class InvalidFileException(OCRException):
    """Unsupported file"""
    pass


class PDFConversionException(OCRException):
    """PDF could not be converted"""
    pass


class ImageReadException(OCRException):
    """Image could not be read"""
    pass