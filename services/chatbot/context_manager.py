
"""
Context Manager
---------------
Fetches tax-related context belonging to a specific user.
"""

import json
import logging

from database.models import (
    User,
    TaxCalculation,
    Recommendation,
    Deduction,
    Document,
    OCRData,
)

logger = logging.getLogger(__name__)


class ContextManager:

    @staticmethod
    def get_context(user_id):
        user = User.query.get(user_id)

        if user is None:
            raise ValueError("User account was not found.")

        # Latest saved tax calculation for this user's documents.
        tax = (
            TaxCalculation.query
            .join(
                Document,
                TaxCalculation.document_id == Document.id,
            )
            .filter(Document.user_id == user_id)
            .order_by(
                TaxCalculation.created_at.desc(),
                TaxCalculation.id.desc(),
            )
            .first()
        )

        deductions = (
            Deduction.query
            .filter_by(user_id=user_id)
            .all()
        )

        recommendations = (
            Recommendation.query
            .filter_by(user_id=user_id)
            .order_by(Recommendation.created_at.desc())
            .limit(10)
            .all()
        )

        documents = (
            Document.query
            .filter_by(user_id=user_id)
            .order_by(
                Document.upload_date.desc(),
                Document.id.desc(),
            )
            .limit(10)
            .all()
        )

        ocr_documents = []

        for document in documents:
            # Get the latest OCR record for this document.
            ocr = (
                OCRData.query
                .filter_by(document_id=document.id)
                .order_by(
                    OCRData.processed_at.desc(),
                    OCRData.id.desc(),
                )
                .first()
            )

            if not ocr:
                continue

            # Include structured entities when available.
            try:
                entities = json.loads(ocr.entities or "{}")
                if not isinstance(entities, dict):
                    entities = {}
            except (TypeError, json.JSONDecodeError):
                entities = {}

            ocr_documents.append({
                "document_type": document.document_type,
                "file_name": document.file_name,
                "ocr_status": document.ocr_status,
                "entities": entities,
                "text": (ocr.clean_text or "")[:2000],
            })

        context = {
            "name": user.name or "",
            "email": user.email or "",

            # None means no saved calculation is available.
            "tax_calculation_available": tax is not None,
            "gross_salary": tax.gross_salary if tax else None,
            "taxable_income": tax.taxable_income if tax else None,
            "total_deductions": tax.total_deductions if tax else None,
            "old_tax": tax.old_regime_tax if tax else None,
            "new_tax": tax.new_regime_tax if tax else None,
            "recommended_regime": tax.recommended_regime if tax else None,
            "tax_saved": tax.tax_saved if tax else None,

            "deductions": [
                {
                    "section": deduction.section,
                    "amount": deduction.amount,
                    "financial_year": deduction.financial_year,
                    "status": deduction.status,
                }
                for deduction in deductions
            ],

            "recommendations": [
                recommendation.recommendation
                for recommendation in recommendations
                if recommendation.recommendation
            ],

            "documents": ocr_documents,
        }

        return context
