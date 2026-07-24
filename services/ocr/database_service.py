"""
database_service.py
-------------------

Handles saving OCR results to the database.

Author: CAAI Team
"""

import json

from database.database import db
from database.models import OCRData, Document

from services.ocr.logger import logger


class OCRDatabaseService:

    def save(
        self,
        document_id,
        raw_text,
        clean_text,
        entities,
        confidence,
        valid=True,
        missing=None,
        errors=None
    ):
        """
        Save OCR results into OCRData table
        and update the corresponding Document.
        """

        try:

            if missing is None:
                missing = []

            if errors is None:
                errors = []

            # -----------------------------
            # Save OCRData
            # -----------------------------

            ocr_data = OCRData(

                document_id=document_id,

                raw_text=raw_text,

                clean_text=clean_text,

                entities=json.dumps(entities, indent=4),

                confidence=confidence

            )

            db.session.add(ocr_data)

            # -----------------------------
            # Update Document
            # -----------------------------

            document = Document.query.get(document_id)

            if document:

                if valid:

                    document.ocr_status = "Completed"

                    document.processed = True

                else:

                    document.ocr_status = "Validation Failed"

                    document.processed = False

            db.session.commit()

            logger.info(
                f"OCR data saved successfully for document {document_id}"
            )

            return True

        except Exception as e:

            db.session.rollback()

            logger.error(str(e))

            raise