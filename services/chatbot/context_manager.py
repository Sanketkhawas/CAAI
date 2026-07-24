"""
Context Manager
---------------
Fetches user data from database.
"""

from database.models import (
    User,
    TaxCalculation,
    Recommendation,
    Deduction,
    Document,
    OCRData
)


class ContextManager:

    @staticmethod
    def get_context(user_id):

        user = User.query.get(user_id)

        tax = TaxCalculation.query.filter_by(
            user_id=user_id
        ).first()

        deductions = Deduction.query.filter_by(
            user_id=user_id
        ).all()

        recommendations = Recommendation.query.filter_by(
            user_id=user_id
        ).all()

        documents = Document.query.filter_by(
            user_id=user_id
        ).all()

        ocr_documents = []

        for document in documents:

            ocr = OCRData.query.filter_by(
                document_id=document.id
            ).first()

            if ocr:

                ocr_documents.append({

                "document_type": document.document_type,

                "text": ocr.clean_text[:3000]

        })

        context = {

            "name": user.name if user else "",

            "email": user.email if user else "",

            "old_tax":
                tax.old_regime_tax if tax else 0,

            "new_tax":
                tax.new_regime_tax if tax else 0,

            "recommended_regime":
                tax.recommended_regime if tax else "",

            "tax_saved":
                tax.tax_saved if tax else 0,

            "deductions":
                [
                    {
                        "section": d.section,
                        "amount": d.amount
                    }

                    for d in deductions
                ],

            "recommendations":

                [
                    r.recommendation

                    for r in recommendations
                ],

                "documents": ocr_documents
        }

        return context